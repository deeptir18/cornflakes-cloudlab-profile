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

sudo su - $GENIUSER -c 'curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y'
sudo su - $GENIUSER -c 'rustup install 1.70.0'
sudo su - $GENIUSER -c 'rustup default 1.70.0'
sudo su - $GENIUSER -c 'rustup component add rustfmt'
sudo su - $GENIUSER -c 'rustup default stable'
