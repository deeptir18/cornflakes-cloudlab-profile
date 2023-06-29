USER=$1
su - $USER -c  "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y"
su - $USER -c "rustup install 1.70.0"
su - $USER -c "rustup default 1.70.0"
su - $USER -c "rustup component add rustfmt"
su - $USER -c "rustup default stable"
