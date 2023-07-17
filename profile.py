"""This is a trivial example of a gitrepo-based profile; The profile source code and other software, documentation, etc. are stored in in a publicly accessible GIT repository (say, github.com). When you instantiate this profile, the repository is cloned to all of the nodes in your experiment, to `/local/repository`. 

This particular profile is a simple example of using a single raw PC. It can be instantiated on any cluster; the node will boot the default operating system, which is typically a recent version of Ubuntu.

Instructions:
Wait for the profile instance to start, then click on the node in the topology and choose the `shell` menu item. 
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Emulab extensions.
import geni.rspec.emulab as emulab 

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()
ubuntu_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD'

pc.defineParameter("dataset", "Your dataset URN",
                   portal.ParameterType.STRING,
                   "urn:publicid:IDN+utah.cloudlab.us:demeter-pg0+ltdataset+cornflakes-data")

pc.defineParameter("phystype",
                    "Physical Node Type",
                    portal.ParameterType.STRING,
                    "c6525-100g", 
                    legalValues=["c6525-100g", "d6515", "c6525-25g"]
                    )
pc.defineParameter("nfsphystype",
                    "Physical Node Type for NFS server",
                    portal.ParameterType.STRING,
                    "c6525-25g", 
                    legalValues=["c6525-100g", "d6515", "c6525-25g"]
                    )
pc.defineParameter("numclients",
                    "Number of clients to spawn (max 5)",
                    portal.ParameterType.INTEGER,
                    1, 
                    )

pc.defineParameter("sameSwitch",  "No Interswitch Links", portal.ParameterType.BOOLEAN, False,
                    advanced=True,
                    longDescription="Sometimes you want all the nodes connected to the same switch. " +
                    "This option will ask the resource mapper to do that, although it might make " +
                    "it imppossible to find a solution. Do not use this unless you are sure you need it!")

# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()
pc.verifyParameters()

# NFS network
# Do not change these unless you change the setup scripts too.
nfsServerName = "nfs"
nfsLanName    = "nfsLan"
nfsDirectory  = "/nfs"
nfsLan = request.LAN(nfsLanName)
nfsLan.best_effort       = True
nfsLan.vlan_tagging      = True
nfsLan.link_multiplexing = True

## setup nfs server
nfsServer = request.RawPC(nfsServerName)
nfsServer.disk_image = ubuntu_image
nfsServer.hardware_type = params.nfsphystype

# Attach server to lan.
nfsLan.addInterface(nfsServer.addInterface())
# Initialization script for the server nfs
nfsServer.addService(pg.Execute(shell="sh", command="sudo /bin/bash /local/repository/nfs-server.sh"))

# Special node that represents the ISCSI device where the dataset resides
dsnode = request.RemoteBlockstore("dsnode", nfsDirectory)
dsnode.dataset = params.dataset
# Link between the nfsServer and the ISCSI device that holds the dataset
dslink = request.Link("dslink")
dslink.addInterface(dsnode.interface)
dslink.addInterface(nfsServer.addInterface())
# Special attributes for this link that we must use.
dslink.best_effort = True
dslink.vlan_tagging = True
dslink.link_multiplexing = True


## Setup cornflakes nodes
ip_addrs = ['192.168.1.1', '192.168.1.2', '192.168.1.3', '192.168.1.4', '192.168.1.5', '192.168.1.6']
# link
link_0 = request.LAN('link-0')
if params.sameSwitch:
    link_0.setNoInterSwitchLinks()
link_0.Site('undefined')
if params.phystype == "c6525-25g":
    link_0.bandwidth = 25000000
else:
    link_0.bandwidth = 100000000
link_0.addComponentManager('urn:publicid:IDN+utah.cloudlab.us+authority+cm')

# Node cornflakes0 (server)
node_cornflakes0 = request.RawPC('cornflakes-server')
node_cornflakes0.hardware_type = params.phystype
node_cornflakes0.disk_image = ubuntu_image
iface0 = node_cornflakes0.addInterface('interface-0', pg.IPv4Address(ip_addrs[0],'255.255.255.0'))
link_0.addInterface(iface0)

nodes = [node_cornflakes0]

# clients
for i in range(params.numclients):
    machine_name = "cornflakes-client{}".format(str(i+1))
    iface_name = "interface-{}".format(str(i+1))
    node = request.RawPC(machine_name)
    node.hardware_type = params.phystype
    node.disk_image = ubuntu_image
    iface = node.addInterface(iface_name, pg.IPv4Address(ip_addrs[i+1],'255.255.255.0'))
    link_0.addInterface(iface)
    nodes.append(node)

for node in nodes:
    ## do NFS installation
    nfsLan.addInterface(node.addInterface())
    # Initialization script for the clients
    node.addService(pg.Execute(shell="sh", command="sudo /bin/bash /local/repository/nfs-client.sh"))
    
for node in nodes:
    ## install mount point && generate ssh keys
    node.addService(pg.Execute(shell="bash",
        command="/local/repository/ssh.sh"))
    node.addService(pg.Execute(shell="bash",
        command="/local/repository/mount.sh"))

    ## run ubuntu (apt-get) installs and python installs
    node.addService(pg.Execute(shell="bash",
        command="/local/repository/install-dependencies.sh"))

    ## install rust
    node.addService(pg.Execute(shell="bash",
        command="/local/repository/install-rust.sh"))

    ## install local python depedencies
    node.addService(pg.Execute(shell="bash",
        command="/local/repository/install-rust.sh"))

    ## install graphing utilities
    node.addService(pg.Execute(shell="bash", 
        command="REPO_LOCATION=/local/repository /local/repository/install-R.sh"))

    ## download and install protobuf, flatbuffers, capnproto
    node.addService(pg.Execute(shell="bash",
        command="/local/repository/install-libraries.sh /mydata/packages"))
    
    ## TODO: setup config file

    ## copy data from NFS to local repository
    node.addService(pg.Execute(shell="bash",
        command="/local/repository/copy_data.sh"))

    ## clone cornflakes
    node.addService(pg.Execute(shell="bash",
        command="/local/repository/clone_cornflakes.sh"))

    ## download mellanox drivers and reboot the machine
    ## TODO: install mellanox drivers
    node.addService(pg.Execute(shell="bash",
        command="/local/repository/download-mlx5.sh /mydata/packages"))


# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)
