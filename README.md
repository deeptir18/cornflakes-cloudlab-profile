This is a repository-based Cloudlab profile that creates a Cloudlab cluster
ready to run experiments for Cornflakes, a serialization library that offloads
data movement into the NIC.

### Machines
This profile instantiates 2 or 3 c6525-100g machines or d6515 machines (one as
server, the rest as clients); these machines are connected by CX-5 NICs.

### Datasets
To reproduce experiments in the paper, we have provided a cloudlab dataset that
will be mounted onto the folder `/nfs` in the server machine; the cloudlab
startup script scp's data locally for running experiments.

### Setup scripts
The setup scripts (automatically invoked at experiment creation):
1. Setup cluster of 2-3 machines connected on a 100GB link or 25Gb link. The IP addresses for
   the experiments will be 192.168.1.1, 192.168.1.2, and 192.168.1.3; the exact
   interface for the network depends on the machine type (c6525-100g/25g, or
   d6515).
2. Mount dataset onto `/nfs` using dataset parameter provided.
3. Give machines ssh access to each other (required to run the experiments
   later).
3. Install all ubuntu packages (using apt-get) required to build and run
   Cornflakes.
4. Install all R packages and python packages needed to run experiments and
   graph results for reproducibility.
5. Download protobuf, capnproto and flatbuffers (baselines) into
   `/mydata/packages/` and install locally.
6. Download specific version of Mellanox drivers into `/mydata/packages/` and
   install locally. Reboot required (manually) after to load new drivers.



