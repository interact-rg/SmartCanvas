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
`sudo echo "" ; nohup sudo docker compose up &`

Lead with `sudo echo` for caching user password.
https://en.wikipedia.org/wiki/Nohup

Docker compose process (there were multiple processes) can be stopped with:
`sudo kill <process_id>`
in case of no effect, you can try:
`sudo kill -9 <process_id>`
This results in stopping all SmartCanvas containers.

The process ID can be found with:
`ps aux | grep -i compose`

The legend of `ps` output can be checked with:
`ps aux | head`
and a detailed description of 'STAT' column for example can be found with:
`man ps`

## Allow inbound traffic to port 5173 in firewall rules
Add a new TCP rule to security group attached to the virtual machine instance running the containers.<br>
https://docs.csc.fi/cloud/pouta/launch-vm-from-web-gui/#firewalls-and-security-groups
