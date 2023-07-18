#!/bin/bash
set -x
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
sudo su - $GENIUSER -c "mkdir /mydata/$GENIUSER/data"
sudo su - $GENIUSER -c "scp -r deeptir@cornflakes-server:/nfs/expdata/* /mydata/$GENIUSER/data"

