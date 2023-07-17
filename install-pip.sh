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

sudo su - $GENIUSER -c 'pip3 install --user colorama gitpython tqdm parse'
sudo su - $GENIUSER -c 'pip3 install --user setuptools_rust'
sudo su - $GENIUSER -c 'pip3 install --user fabric==2.6.0'
sudo su - $GENIUSER -c 'pip3 install --user pyelftools'
sudo su - $GENIUSER -c 'pip3 install --user numpy pandas'
sudo su - $GENIUSER -c 'pip3 install --user agenda toml'
sudo su - $GENIUSER -c 'pip3 install --user result'
