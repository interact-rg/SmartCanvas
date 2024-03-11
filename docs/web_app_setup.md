# Setup instructions for smart canvas server

Download Ubuntu server image from https://ubuntu.com/download/server

Allocate at least a 20gb virtual hard drive for the machine.

Deploy to CSC Pouta.

If installation gets stuck when deploying to Pouta, you can first download the image to your local machine and do the installation on your local machine and then deploy that to Pouta.

Associate a floating ip for your machine.

Open SSH access for your ip in the security groups and open access to port 5000 for all IP-addresses (0.0.0.0)

# Clone SmartCanvas to your server:

```console
git clone git@github.com:interact-rg/SmartCanvas.git
```
Or from your own fork of the project.

# Run the following commands on the server

First enable flask port in firewall:

```console
sudo ufw allow 5000
```

Then launch the server

```console
make init
make web
```

# The server should now work and is accessed via the floatingip:port combination.

To keep the server running after exiting the terminal you can use screen or nohup when starting the application.

```console
nohup make web &
```

or alternatively

```console
nohup make web
```

```console
sudo apt update
sudo apt install screen
screen
screen -S session_name
```
and then start the application with make web.
