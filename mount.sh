#!/bin/bash
# Create the user SSH directory, just in case.
USERS="root `ls /users`"

# Setup password-less ssh between nodes
for user in $USERS; do
    if [ "$user" = "root" ]; then
        ssh_dir=/root/.ssh
    else
        ssh_dir=/users/$user/.ssh
    fi
    mkdir $ssh_dir && chmod 700 $ssh_dir
    /usr/bin/geni-get key > $ssh_dir/id_rsa
    chmod 600 $ssh_dir/id_rsa
    chown $user: $ssh_dir/id_rsa
    ssh-keygen -y -f $ssh_dir/id_rsa > $ssh_dir/id_rsa.pub
    cat $ssh_dir/id_rsa.pub >> $ssh_dir/authorized_keys2
    chmod 644 $ssh_dir/authorized_keys2
    cat >>$ssh_dir/config <<EOL
    Host *
         StrictHostKeyChecking no
EOL
    chmod 644 $ssh_dir/config
done


# make mount /mydata
sudo mkdir -p /mydata
sudo /usr/local/etc/emulab/mkextrafs.pl /mydata
sudo mkdir /mydata/packages
## make it writeable by everyone??
sudo chmod 775 /mydata/packages

