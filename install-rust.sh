USERS="root `ls /users`"
for user in $USERS; do
    su - $user -c  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    su - $user -c rustup install 1.70.0
    su - $user -c rustup default 1.70.0
    su - $user -c rustup component add rustfmt
    su - $user -c rustup default stable
done
