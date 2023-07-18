#!/bin/bash
set -x
SCRIPTNAME=$0
#
# Might not be on the local cluster, so need to use the urn to
# see who the actual creator is.
#
GENIUSER=`geni-get user_urn | awk -F+ '{print $4}'`
if [ $? -ne 0 ]; then
echo "ERROR: could not run geni-get user_urn!"
exit 1
fi

sudo mkdir -p /mydata/$GENIUSER
sudo chown $GENIUSER: /mydata/$GENIUSER
cd /mydata/$GENIUSER/
sudo su - $GENIUSER -c "git clone https://github.com/deeptir18/cornflakes-scripts.git --recursive /mydata/$GENIUSER/cornflakes-scripts"
sudo su - $GENIUSER -c "git clone https://github.com/deeptir18/cornflakes.git --recursive /mydata/$GENIUSER/cornflakes"
cd /mydata/$GENIUSER/cornflakes
## make submodules (mlx5 drivers package + dpdk)
sudo su - $GENIUSER -c "cd /mydata/$GENIUSER/cornflakes && make submodules CONFIG_MLX5=y"
## build kv app (for comparing cornflakes to protobuf, capnproto and flatbuffers)
sudo su - $GENIUSER -c "cd /mydata/$GENIUSER/cornflakes && make kv CONFIG_MLX5=y CONFIG_DPDK=y"
## build redis (for comparing cornflakes in redis to redis serialization in redis)
sudo su - $GENIUSER -c "cd /mydata/$GENIUSER/cornflakes && make redis CONFIG_MLX5=y CONFIG_DPDK=y"
## build 
sudo su - $GENIUSER -c "cd /mydata/$GENIUSER/cornflakes && make ds-echo CONFIG_MLX5=y CONFIG_DPDK=y"



