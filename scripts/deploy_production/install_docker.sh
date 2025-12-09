#!/bin/bash

set -e

echo "Installing Docker"

./install_docker_apt_repository.sh
./install_docker_packages.sh
./run_docker_hello_world.sh

echo "Done installing Docker"
