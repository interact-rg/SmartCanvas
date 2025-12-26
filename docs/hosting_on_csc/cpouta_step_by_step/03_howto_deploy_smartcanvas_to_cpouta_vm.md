# Deploy SmartCanvas to cPouta virtual machine

## Table of contents

1. [If virtual machine does not have lots of RAM, add swap space](#if-virtual-machine-does-not-have-lots-of-ram-add-swap-space)
1. [Codebase update script](#codebase-update-script)
1. [Application start script](#application-start-script)
    1. [About the start script](#about-the-start-script)
1. [Application stop script](#application-stop-script)
1. [Host management cheatsheet](#host-management-cheatsheet)

[UNTESTED]

The instructions for getting SmartCanvas running on an existing cPouta virtual machine follow.

## If virtual machine does not have lots of RAM, add swap space

You can check memory consumption with: `free -m` .

For adding a swapfile and configuring swap to be enabled on boot due to a new `/etc/fstab` entry, check out:<br>
https://www.digitalocean.com/community/tutorials/how-to-add-swap-space-on-ubuntu-20-04
<br>Command `sudo findmnt --verify` can be used to verify fstab correctness.

## Firewall rule additions

For successfully serving the application, add the following firewall rules:
```
Direction   'Ether Type'    'IP Protocol'   'Port Range'    'Remote IP Prefix'
Ingress     IPv4            TCP             80 (HTTP)       0.0.0.0/0
Ingress     IPv4            TCP             443 (HTTPS)     0.0.0.0/0
```

## Codebase update script

To do this manually instead:
1. Remove old clone
1. Clone
1. Checkout
1. Continue to adjusting `config.sh` if needed

For updating the most recent available versions of SmartCanvas to the virtual
machine and selecting the version by setting `DEPLOYMENT_REF`, you can run
the following command (single command spanning multiple lines that can be pasted
to commandline) for generating an update script:
```bash
tee update_smartcanvas.sh << HEREDOC
#!/bin/bash
set -e
DEFAULT_DEPLOYMENT_REF=""
DEPLOYMENT_REF="\${DEPLOYMENT_REF:=\${DEFAULT_DEPLOYMENT_REF}}"
test -z "\${DEPLOYMENT_REF}" && echo Please set DEPLOYMENT_REF && exit 1
which git || sudo apt -y install git
test -d repositories || mkdir repositories
test -d ./repositories/SmartCanvas && rm -r -f ./repositories/SmartCanvas
git clone https://github.com/interact-rg/SmartCanvas.git ./repositories/SmartCanvas
cd ./repositories/SmartCanvas
git checkout \${DEPLOYMENT_REF} || git checkout -b \${DEPLOYMENT_REF} origin/\${DEPLOYMENT_REF}
echo -e "\nPlease setup ./repositories/SmartCanvas/scripts/deploy_production/config.sh\n"
HEREDOC
```

And then run the generated update script:<br>
```bash
DEPLOYMENT_REF="wanted_target_branch" bash update_smartcanvas.sh
```

## Application start script

For starting the application, a command can be ran for generating a start
script:
```bash
tee start_smartcanvas.sh << HEREDOC
#!/bin/bash
set -e
cd ./repositories/SmartCanvas
nohup ./scripts/deploy_production/production_start.sh &> \
    ./scripts/deploy_production/start.log &
HEREDOC
```

To run the generated start script:<br>
```bash
bash start_smartcanvas.sh
```

To follow the progress of start script:<br>
```bash
tail -f ./repositories/SmartCanvas/scripts/deploy_production/start.log
```

### About the start script

SmartCanvas repository contains a deployment script that can be used for
launching the application in a reproducible way in the production
environment:<br>
`scripts/deploy_production/production_start.sh`<br>
Also invoked in the generated start script above.

Please insert the domain name of your virtual machine into:<br>
`scripts/deploy_production/config.sh`<br>
before executing the deployment script.<br>

The default configuration with `CONTAINER_REMOVE_ENABLED` and
`IMAGE_REMOVE_ENABLED` set to 'TRUE' has been tested. This configuration has the
benefit of allowing variant to be changed and deployed in the next run. It is
also unambiguous what was the version running in the latest deployment. There is
currently no support for reusing previously stopped containers.

The script has the intent of starting two background processes. One process for
running backend Docker container and another process for running a reverse
proxy, serving the application over HTTPS. Camera usage requires HTTPS. At the
core are these two commands:
* `nohup sudo docker run -p 5000:5000 "smartcanvas_backend:latest" &> $(pwd)/backend.log &`
* `nohup sudo caddy reverse-proxy --from "fip-86-50-168-120.kaj.poutavm.fi" --to :5000 &> $(pwd)/caddy.log &`

https://caddyserver.com/docs/quick-starts/reverse-proxy#https-from-client-to-proxy

The `nohup` utility is used to avoid the background processes being terminated
when exiting from a shell that was used for starting the background processes.<br>
https://en.wikipedia.org/wiki/Nohup

The processes write their log to:
* `./scripts/deploy_production/backend.log`
* `./scripts/deploy_production/caddy.log`

A live feed of the logs can be achieved with: `tail -f <logfile>`, Ctrl-C to exit.

When the processes have had enough time to execute, the application can be
accessed by giving the virtual machine domain name to a web browser and
connecting. The backend container serves the built frontend to connecting
clients.

## Application stop script

For stopping the application, a command can be ran for generating a stop
script:
```bash
tee stop_smartcanvas.sh << HEREDOC
#!/bin/bash
set -e
cd ./repositories/SmartCanvas
./scripts/deploy_production/production_stop.sh \
    | tee ./scripts/deploy_production/stop.log
HEREDOC
```

To run the generated stop script:<br>
```bash
bash stop_smartcanvas.sh
```

## Host management cheatsheet

Check computation resource usage:<br>
`top`<br>
use 'q' to exit.

Free space taken up by Docker resources
sudo docker system prune

Free space taken up by poetry
rm -r ~/.cache/pypoetry/

Check Docker container statuses:<br>
`sudo docker container ps -a`

Stop running containers:<br>
`sudo docker container stop <container name/ID>`

Check existing Docker images:<br>
`sudo docker image ls`

Remove Docker image:<br>
`sudo docker image rm <image>`

Filter running processes using:<br>
`ps aux | grep -i <process name>`

Terminate proceesses using:<br>
`pkill <process name>`
`kill <process ID>`
or the more forceful:<br>
`kill -9 <process ID>`

Check command documentation:<br>
`man <command>`<br>
To search in man pages, press '/' and give a search term. Cycle through matches
using 'n' and 'N'.<br>
`<command> --help`
`help <command>`
