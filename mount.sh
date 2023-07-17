#!/bin/bash

# make mount /mydata
sudo mkdir -p /mydata
sudo /usr/local/etc/emulab/mkextrafs.pl /mydata
sudo mkdir /mydata/packages
## make it writeable by everyone??
sudo chmod 775 /mydata/packages

