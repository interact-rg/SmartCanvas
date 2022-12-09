# Setup instructions for smart canvas server

Download Ubuntu server image from https://ubuntu.com/download/server

Allocate at least a 20gb virtual hard drive for the machine.

Deploy to CSC Pouta.

If installation gets stuck when deploying to Pouta, you can first download the image to your local machine and do the installation on your local machine and then deploy that to Pouta.

Associate a floating ip for your machine.

Open SSH access for your ip in the security groups and open access to port 5000 for all IP-addresses (0.0.0.0)

# Run the following commands on the server

```console
make init
make web
```

# The server should now work and is accessed via the <floating ip>:<port> combination. 