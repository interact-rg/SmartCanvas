# Deploy SmartCanvas to cPouta virtual machine

TODO link to all CSC step-by-step documents in top level README.md

## If virtual machine does not have lots of RAM, add swap space
For adding a swapfile and configuring swap to be enabled on boot due to a new `/etc/fstab` entry, check out:<br>
https://www.digitalocean.com/community/tutorials/how-to-add-swap-space-on-ubuntu-20-04

## Install Docker
https://docs.docker.com/engine/install/ubuntu/

## Clone repository
`git clone https://github.com/interact-rg/SmartCanvas.git`

## Start all SmartCanvas docker containers
`nohup docker compose up &`

## Allow inbound traffic to port 5173 in firewall rules
Add a new TCP rule to security group attached to the virtual machine instance running the containers.<br>
https://docs.csc.fi/cloud/pouta/launch-vm-from-web-gui/#firewalls-and-security-groups
