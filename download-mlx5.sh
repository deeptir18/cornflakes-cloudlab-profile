#!/bin/bash
pushd $PACKAGES
wget https://content.mellanox.com/ofed/MLNX_OFED-5.6-2.0.9.0/MLNX_OFED_LINUX-5.6-2.0.9.0-ubuntu20.04-x86_64.tgz --no-check-certificate
tar -xzf MLNX_OFED_LINUX-5.6-2.0.9.0-ubuntu20.04-x86_64.tgz 
popd

