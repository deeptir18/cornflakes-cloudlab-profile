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
    sudo su - $user -c "mkdir ${ssh_dir} && chmod 700 ${ssh_dir}"
    sudo su - $user -c "/usr/bin/geni-get key > ${ssh_dir}/id_rsa"
    sudo su - $user -c "chmod 600 ${ssh_dir}/id_rsa"
    sudo su - $user -c "chown $user: ${ssh_dir}/id_rsa"
    sudo su - $user -c "ssh-keygen -y -f ${ssh_dir}/id_rsa > ${ssh_dir}/id_rsa.pub"
    sudo su - $user -c "cat ${ssh_dir}/id_rsa.pub >> $ssh_dir/authorized_keys2"
    sudo su - $user -c "echo -e '\\nHost * \\n\\tStrictHostKeyChecking no\\n' >> ${ssh_dir}/config"
    sudo su - $user -c "chmod 644 ${ssh_dir}/config"
done
