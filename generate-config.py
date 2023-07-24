import argparse
from fabric import Connection
import agenda
import os
import shutil
import subprocess
import sys
import threading
import time
import toml
import yaml as pyyaml
SSH_IP_INTERFACE = "eno33np0"
class ConnectionWrapper(Connection):
    def __init__(self, addr, user=None, port=22, key=None):
        connect_kwargs = {}
        if key is not None:
            connect_kwargs["key_filename"] = [key]
            connect_kwargs["banner_timeout"] = 200
        super().__init__(
            host = addr,
            user = user,
            port = port,
            forward_agent = True,
            connect_kwargs = connect_kwargs,
        )
        self.addr = addr
        self.conn_addr = addr

        # Start the ssh connection
        super().open()

    def get_addr(self):
        return self.addr
    """
    Run a command on the remote machine
    verbose    : if true, print the command before running it, and any output it produces
                 (if not redirected)
                 if false, capture anything produced in stdout and save in result (res.stdout)
    background : if true, start the process in the background via nohup.
                 if output is not directed to a file or pty=True, this won't work
    stdin      : string of filename for stdin (default /dev/stdin as expected)
    stdout     : ""
    stderr     : ""
    ignore_out : shortcut to set stdout and stderr to /dev/null
    wd         : cd into this directory before running the given command
    sudo       : if true, execute this command with sudo (done AFTER changing to wd)
    returns result struct
        .exited = return code
        .stdout = stdout string (if not redirected to a file)
        .stderr = stderr string (if not redirected to a file)
    """
    def run(self, cmd, *args, stdin=None, stdout=None, stderr=None, ignore_out=False, wd=None, sudo=False, background=False, quiet=False, pty=True, **kwargs):
        self.verbose = True
        # Prepare command string
        pre = ""
        if wd:
            pre += f"cd {wd} && "
        if background:
            pre += "screen -d -m "
        #escape the strings
        cmd = cmd.replace("\"", "\\\"")
        if sudo:
            pre += "sudo "
        pre += "bash -c \""
        if ignore_out:
            stdin="/dev/null"
            stdout="/dev/null"
            stderr="/dev/null"
        if background:
            stdin="/dev/null"

        full_cmd = f"{pre}{cmd}"
        if stdout is not None:
            full_cmd  += f" > {stdout} "
        if stderr is not None:
            full_cmd  += f" 2> {stderr} "
        if stdin is not None:
            full_cmd  += f" < {stdin} "

        full_cmd += "\""

        # Prepare arguments for invoke/fabric
        if background:
            pty=False

        # Print command if necessary
        if not quiet:
            agenda.subtask("[{}]{} {}".format(self.addr.ljust(10), " (bg) " if background else "      ", full_cmd))

        # Finally actually run it
        return super().run(full_cmd, *args, hide=True, warn=True, pty=pty, **kwargs)

    def file_exists(self, fname):
        res = self.run(f"ls {fname}")
        return res.exited == 0

    def prog_exists(self, prog):
        res = self.run(f"which {prog}")
        return res.exited == 0

    def check_proc(self, proc_name, proc_out):
        res = self.run(f"pgrep {proc_name}")
        if res.exited != 0:
            agenda.subfailure(f'failed to find running process with name \"{proc_name}\" on {self.addr}')
            res = self.run(f'tail {proc_out}')
            if res.exited == 0:
                print(res.command)
                print(res.stdout)
            else:
                print(res)
            sys.exit(1)


    def check_file(self, grep, where):
        res = self.run(f"grep \"{grep}\" {where}")
        if res.exited != 0:
            agenda.subfailure(f"Unable to find search string (\"{grep}\") in process output file {where}")
            res = self.run(f'tail {where}')
            if res.exited == 0:
                print(res.command)
                print(res.stdout)
            sys.exit(1)

    def local_path(self, path):
        r = self.run(f"ls {path}")
        return r.stdout.strip().replace("'", "")

    def put(self, local_file, remote=None, preserve_mode=True):
        if remote and remote[0] == "~":
            remote = remote[2:]
        agenda.subtask("[{}] scp localhost:{} -> {}:{}".format(
            self.addr,
            local_file,
            self.addr,
            remote
        ))

        return super().put(local_file, remote, preserve_mode)

    def get(self, remote_file, local=None, preserve_mode=True):
        if local is None:
            local = remote_file

        agenda.subtask("[{}] scp {}:{} -> localhost:{}".format(
            self.addr,
            self.addr,
            remote_file,
            local
        ))

        return super().get(remote_file, local=local, preserve_mode=preserve_mode)

def get_local(filename, local=None, preserve_mode=True):
    assert(local is not None)
    subprocess.run(f"mv {filename} {local}", shell=True)


def check(ok, msg, addr, allowed=[]):
    # exit code 0 is always ok, allowed is in addition
    if ok.exited != 0 and ok.exited not in allowed:
        agenda.subfailure(f"{msg} on {addr}: {ok.exited} not in {allowed}")
        agenda.subfailure("stdout")
        print(ok.stdout)
        agenda.subfailure("stderr")
        print(ok.stderr)
        global thread_ok
        thread_ok = False # something went wrong.
        raise Exception(f"{msg} on {addr}: {ok.exited} not in {allowed}")


def main():
    parser = argparse.ArgumentParser(prog='generate config')
    parser.add_argument('--machine',
                        required=True,
                        help = "Either cornflakes-server, cornflakes-client1, or cornflakes-clientn")
    parser.add_argument('--num_clients',
            type=int,
            default=1)
    parser.add_argument("--user",
            required=True)
    parser.add_argument("--outfile",
            required=True)
    ## need to get map from machine IP to machine name
    args = parser.parse_args()
    machine_map = get_machine_map(args.user, args.num_clients)
    conns = {}
    for machine_name in machine_map:
        conns[machine_name] = setup_conn(args, machine_map, machine_name)
    yaml = build_yaml(args, conns, machine_map)
    # write yaml to yaml out
    with open(args.outfile, 'w') as outfile:
        pyyaml.dump(yaml, outfile, default_flow_style=False)




def build_yaml(args, conns, machine_map):
    machines = [("192.168.1.1", "cornflakes-server")]
    for i in range(0, args.num_clients):
        machines.append((f"192.168.1.{i+2}",
        f"cornflakes-client{i+1}"))
    info_map = {}
    yaml = {}
    yaml_clients = ["client{}".format(i) for i in range(1, args.num_clients
        + 1)]
    yaml_server = ["server"]
    yaml["host_types"] = {"server": yaml_server, "client": yaml_clients}

    yaml_dpdk = {}
    yaml_mlx5 = {}
    hosts = {}
    lwip_known_hosts = {}
    for machine_ip in machines:
        ip_address = machine_ip[0]
        machine = machine_ip[1]
        conn = conns[machine]
        interface_command = f"ifconfig | grep -B1 \"{ip_address}\" | awk \'{{print $first}}\'"
        # 1 : task 1: get the right interface
        our_conn = conns[machine]
        interface = our_conn.run(interface_command).stdout.split(" ")[0][:-1]
        mac_command = f"ifconfig {interface} | grep 'ether'"
        pci_command = f"ethtool -i {interface} | grep 'bus-info'"
        mac_address = our_conn.run(mac_command).stdout.strip().split(" ")[1]
        pci_address = our_conn.run(pci_command).stdout.strip().split(": ")[1]
        port = int(pci_address[-1])
        agenda.task(f"[{machine}: {machine_ip}] interface: {interface},"\
                f" mac: {mac_address}, pci: {pci_address}, port: {port}")
        ## fill in info about this machine's interface
        if machine == args.machine:
            # run jumbo frames configuration
            yaml_dpdk["eal_init"] = [f"-c", f"0xff", f"-n", f"8", 
                                    f"-a",f"{pci_address}",f"--proc-type=auto"]
            yaml_dpdk["pci_addr"] = f"{pci_address}"
            yaml_dpdk["port"] = f"{port}"
            yaml_mlx5["pci_addr"] = f"{pci_address}"
        lwip_known_hosts[mac_address] = f"{ip_address}"
        hosts[machine.split("cornflakes-")[1]] = {
            "addr": f"{machine_map[machine]}",
            "ip": f"{ip_address}",
            "mac": f"{mac_address}",
            "cornflakes_dir": f"/mydata/{args.user}/cornflakes",
            "tmp_folder": f"/mydata/{args.user}/cornflakes_tmp",
            "config_file": f"/mydata/{args.user}/config/cluster_config.yaml"
        }
    yaml["lwip"] = {"known_hosts": lwip_known_hosts}
    yaml["hosts"] = hosts
    yaml["dpdk"] = yaml_dpdk
    yaml["mlx5"] = yaml_mlx5
    yaml["max_clients"] = args.num_clients
    yaml["user"] = args.user
    yaml["cornflakes_dir"] = f"/mydata/{args.user}/cornflakes"
    yaml["port"] = 54321
    yaml["client_port"] = 12345
    return yaml

## find our interface name and 
def get_machine_map(user, num_clients):
    machines = [("192.168.1.1", "cornflakes-server")]
    for i in range(0, num_clients):
        machines.append((f"192.168.1.{i+2}",
        f"cornflakes-client{i+1}"))
    machine_map = {}
    command = 'ifconfig | grep -B1 "{}" | awk \'$1!="inet" && $1!="--" {{print $1}}\''
    for machine_ip in machines:
        ip_address = machine_ip[0]
        machine = machine_ip[1]
        print(ip_address, machine)
        command = f"ip -4 addr show {SSH_IP_INTERFACE} | grep -oP \'(?<=inet\\s)\\d+(\\.\\d+){{3}}\'"
        output = subprocess.Popen(f"ssh {user}@{machine} {command}" ,shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE).communicate()

        machine_map[machine] = output[0].strip().decode('utf-8')
        print(machine_map[machine])
    return machine_map

def setup_conn(args, machine_map, machine_name):
    machine_ip = machine_map[machine_name]
    agenda.task(f"[{machine_name}: {machine_ip}] setup ssh connection")
    conn = ConnectionWrapper(machine_ip, 
                                args.user, 
                                22)
    return conn

if __name__ == '__main__':
    main()
