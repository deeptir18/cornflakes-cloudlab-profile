#!/bin/bash
PACKAGES=$1

pushd $PACKAGES
pushd MLNX_OFED_LINUX-5.6-2.0.9.0-ubuntu20.04-x86_64
sudo ./mlnxofedinstall --upstream-libs --dpdk --force
#sudo /etc/init.d/openibd restart
popd
popd
