#!/bin/bash

set -e

echo "Installing Docker packages"

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "Done installing Docker packages"
