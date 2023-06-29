#!/bin/bash


# Required for protobuf
sudo apt install -y apt-transport-https curl gnupg
curl -fsSL https://bazel.build/bazel-release.pub.gpg | sudo gpg --dearmor | sudo tee /usr/share/keyrings/bazel-archive-keyring.gpg >/dev/null
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/bazel-archive-keyring.gpg] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list
sudo apt update && sudo apt install -y bazel

# install and clone protobuf and flatbuffers and capnproto into this folder
PACKAGES=$1

pushd $PACKAGES
# clone protobuf
git clone https://github.com/protocolbuffers/protobuf.git --recursive
cd protobuf
bazel build :protoc :protobuf
sudo cp bazel-bin/protoc /usr/local/bin
cd ..

# clone flatbuffers
git clone https://github.com/google/flatbuffers.git
cd flatbuffers
git checkout v22.9.24
cmake -G "Unix Makefiles"
make
cd ..
sudo ln -s $PACKAGES/flatbuffers/flatc /usr/local/bin/flatc
chmod +x $PACKAGES/flatbuffers/flatc
flatc --version # sanity check that it works



# clone and build capnproto
curl -O https://capnproto.org/capnproto-c++-0.9.1.tar.gz
tar zxf capnproto-c++-0.9.1.tar.gz
cd capnproto-c++-0.9.1
./configure
make -j6 check
sudo make install
popd
