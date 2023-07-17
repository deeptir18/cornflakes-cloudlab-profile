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

cd /mydata/$GENIUSER/
sudo su - $GENIUSER -c "git clone https://github.com/deeptir18/cornflakes-scripts.git --recursive /mydata/$GENIUSER/cornflakes-scripts"
cd /mydata/$GENIUSER/cornflakes-scripts/cornflakes
sudo su - $GENIUSER -c "cd /mydata/$GENIUSER/cornflakes-scripts/cornflakes && make submodules CONFIG_MLX5=y"
sudo su - $GENIUSER -c "cd /mydata/$GENIUSER/cornflakes-scripts/cornflakes && make kv CONFIG_MLX5=y CONFIG_DPDK=y"
sudo su - $GENIUSER -c "cd /mydata/$GENIUSER/cornflakes-scripts/cornflakes && make redis CONFIG_MLX5=y CONFIG_DPDK=y"
sudo su - $GENIUSER -c "cd /mydata/$GENIUSER/cornflakes-scripts/cornflakes && make ds-echo CONFIG_MLX5=y CONFIG_DPDK=y"



