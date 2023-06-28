"""This is a trivial example of a gitrepo-based profile; The profile source code and other software, documentation, etc. are stored in in a publicly accessible GIT repository (say, github.com). When you instantiate this profile, the repository is cloned to all of the nodes in your experiment, to `/local/repository`. 

This particular profile is a simple example of using a single raw PC. It can be instantiated on any cluster; the node will boot the default operating system, which is typically a recent version of Ubuntu.

Instructions:
Wait for the profile instance to start, then click on the node in the topology and choose the `shell` menu item. 
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()
ubuntu_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD'

## TODO: add loaded dataset containing data to be accessed on /experimentdata/
#pc.defineParameter("dataset", "Your dataset URN",
#                   portal.ParameterType.STRING,
#                   "urn:publicid:IDN+emulab.net:portalprofiles+ltdataset+DemoDataset")

pc.defineParameter("phystype",
                    "Physical Node Type",
                    portal.ParameterType.STRING,
                    "c6525-100g", 
                    legalValues=["c6525-100g", "d6515"]
                    )

pc.defineParameter("sameSwitch",  "No Interswitch Links", portal.ParameterType.BOOLEAN, False,
                    advanced=True,
                    longDescription="Sometimes you want all the nodes connected to the same switch. " +
                    "This option will ask the resource mapper to do that, although it might make " +
                    "it imppossible to find a solution. Do not use this unless you are sure you need it!")

# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()
pc.verifyParameters()

# Node cornflakes0
node_cornflakes0 = request.RawPC('cornflakes0')
node_cornflakes0.hardware_type = params.phystype
node_cornflakes0.disk_image = ubuntu_image
iface0 = node_cornflakes0.addInterface('interface-0', pg.IPv4Address('192.168.1.1','255.255.255.0'))

# Node cornflakes1
node_cornflakes1 = request.RawPC('cornflakes1')
node_cornflakes1.hardware_type = params.phystype
node_cornflakes1.disk_image = ubuntu_image
iface1 = node_cornflakes1.addInterface('interface-1', pg.IPv4Address('192.168.1.2','255.255.255.0'))

# Node cornflakes2
node_cornflakes2 = request.RawPC('cornflakes2')
node_cornflakes2.hardware_type = params.phystype
node_cornflakes2.disk_image = ubuntu_image
iface2 = node_cornflakes2.addInterface('interface-2', pg.IPv4Address('192.168.1.3','255.255.255.0'))

# Link link-0
link_0 = request.LAN('link-0')
if params.sameSwitch:
    link_0.setNoInterSwitchLinks()
link_0.Site('undefined')
link_0.bandwidth = 100000000
link_0.addComponentManager('urn:publicid:IDN+utah.cloudlab.us+authority+cm')
link_0.addInterface(iface0)
link_0.addInterface(iface1)
link_0.addInterface(iface2)

nodes = [node_cornflakes1, node_cornflakes2, node_cornflakes3]
for node in nodes:
    ## install mount point && generate ssh keys
    node.addService(pg.Execute(shell="bash", command="/local/repository/mount.sh")

    ## run ubuntu (apt-get) installs and python installs
    node.addService(pg.Execute(shell="bash", command="/local/repository/install-dependencies.sh")

    ## install Rust
    node.addService(pg.Execute(shell="bash", command="/local/repository/install-rust.sh")

    ## install graphing utilities
    node.addService(pg.Execute(shell="bash", command="/local/repository/install-R.sh"))

    ## download and install protobuf, flatbuffers, capnproto
    node.addService(pg.Execute(shell="bash", command="PRIMARY=y /local/repository/install-libraries.sh /mydata/packages"))

    ## download mellanox drivers
    ## TODO: install mellanox drivers
    node.addService(pg.Execute(shell="bash", command="/local/repository/install-mlx5.sh /mydata/packages"))

# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)
