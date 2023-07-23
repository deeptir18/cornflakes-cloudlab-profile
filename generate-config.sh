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

sudo su - $GENIUSER -c "mkdir /mydata/$GENIUSER/config"
sudo su - $GENIUSER -c "python3 generate-config.py --user $GENIUSER --num_clients $CLIENTS --machine $MACHINE --outfile /mydata/$GENIUSER/config/cluster_config.yaml"

