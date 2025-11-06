# cPouta virtual machine instance creation and access

Here is a short summary of the main actions required for setting up a virtual machine with SSH access over the internet in unmodified cPouta environment.

## If nonexistent, create an SSH keypair on your personal computer
https://docs.csc.fi/cloud/pouta/launch-vm-from-web-gui/#setting-up-ssh-keys

## If you have multiple CSC projects, select the wanted project
https://docs.csc.fi/cloud/pouta/launch-vm-from-web-gui/#selecting-the-csc-project

## If nonexistent, create firewall rules for SSH access
https://docs.csc.fi/cloud/pouta/launch-vm-from-web-gui/#firewalls-and-security-groups

Create a security group and new rule in the group for every IP that needs access to the virtual machine. This group needs to be attached to the instance during or after the launch.

The IP of your current personal computer can be discovered using:<br>
https://apps.csc.fi/myip/

SSH rule creation:
* Rule: SSH
* Remote: CIDR
* CIDR: xxx.xxx.xxx.xxx/32

## Launch a virtual machine instance from an image
https://docs.csc.fi/cloud/pouta/launch-vm-from-web-gui/#launching-a-virtual-machine

Configuration used for a testing virtual machine:
* For source image, our group ended up picking latest Ubuntu.
* The selected flavor had least computing resources (such as RAM and VCPUS).
* The only pre-existing network was kept allocated.
* Network ports were kept as empty.
* Default security group was kept allocated and the group for SSH access should be allocated into use.
* A public SSH key was imported. Do not use the SSH generator of webpage to be strictly compliant with these instructions.
* Admin password was setup (the default account has permission to use `sudo`).
    * It is not known what is the Admin account. There was no `admin` user in `/etc/passwd` and admin password is not the password of `root` user.
* Configuration was kept default.
* Server Groups were kept empty.
* Metadata can be left untouched.

## Attach a public IP address to the virtual machine instance
https://docs.csc.fi/cloud/pouta/launch-vm-from-web-gui/#post-creation-step

Create a new floating IP. When selecting port to be associated, we select the newly created instance.

## Find out the default username of virtual machine
Trying to login as `root` over SSH can output a name of less privileged default username of an account. Use the public floating IP that was created and attached in the previous step.

`ssh root@xxx.xxx.xxx.xxx`

Alternatively check from list of usernames of CSC images:<br>
https://docs.csc.fi/cloud/pouta/images/#images

## Connect to the virtual machine using SSH
Use the public floating IP and username discovered above.
