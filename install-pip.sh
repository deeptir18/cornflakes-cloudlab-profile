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
if [ $USER != $GENIUSER ]; then
sudo -u $GENIUSER $SCRIPTNAME
exit $?
fi
pip3 install --user colorama gitpython tqdm parse
pip3 install --user setuptools_rust
pip3 install --user fabric==2.6.0 
pip3 install --user pyelftools
pip3 install --user numpy pandas
pip3 install --user agenda toml
pip3 install --user result
