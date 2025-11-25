# Deploy SmartCanvas to cPouta virtual machine

[UNTESTED]

The instructions for getting SmartCanvas running on an existing cPouta virtual machine follow.

## If virtual machine does not have lots of RAM, add swap space
You can check memory consumption with: `free -m` .

For adding a swapfile and configuring swap to be enabled on boot due to a new `/etc/fstab` entry, check out:<br>
https://www.digitalocean.com/community/tutorials/how-to-add-swap-space-on-ubuntu-20-04
Command `sudo findmnt --verify` can be used to verify fstab correctness.

## Update to most recent version of the repository

For updating the most recent version of SmartCanvas to the virtual machine,
you can run the following command (single command spanning multiple lines) for
generating an update script:
```bash
tee update_smartcanvas.sh << HEREDOC
#!/bin/bash
set -e
which git || sudo apt -y install git
test -d repositories || mkdir repositories
test -d ./repositories/SmartCanvas && rm -r ./repositories/SmartCanvas
git clone https://github.com/interact-rg/SmartCanvas.git ./repositories/SmartCanvas
echo -e "\nPlease setup ./repositories/SmartCanvas/scripts/deploy_production/config.sh\n"
HEREDOC
```

And then run the generated update script:
`bash update_smartcanvas.sh`

## Execute start script

For starting the application with the version decided by `DEPLOYMENT_BRANCH`, a
command can be ran for generating a script:
```bash
tee start_smartcanvas.sh << HEREDOC
#!/bin/bash
set -e
DEPLOYMENT_BRANCH=""
cd ./repositories/SmartCanvas
test -z "${DEPLOYMENT_BRANCH}" && echo Please set DEPLOYMENT_BRANCH && exit 1
git checkout ${DEPLOYMENT_BRANCH}
./scripts/deploy_production/deploy_production.sh
HEREDOC
```

To run the generated start script:
`bash start_smartcanvas.sh`

SmartCanvas repository contains a deployment script that can be used for
setting up the application in a reproducible way in the production
environment:<br>
`scripts/deploy_production/deploy_production.sh`<br>
Also invoked in the generated start script above.

Please insert the domain name of your virtual machine into:<br>
`scripts/deploy_production/config.sh`<br>
before executing the deployment script.<br>

TODO add branch selection to config.sh

Then to execute, `cd` to the top level of SmartCanvas repository and run:<br>
`./scripts/deploy_production/deploy_production.sh`.

The script has the intent of starting two background processes. One process for
running backend Docker container and another process for running a reverse
proxy, serving the application over HTTPS. Camera usage requires HTTPS.

The `nohup` utility is used to avoid the background processes being terminated
when exiting from a shell that was used for starting the background processes.<br>
https://en.wikipedia.org/wiki/Nohup

The processes write their log to:
* `scripts/backend.log`
* `scripts/caddy.log`

A live feed of the logs can be achieved with: `tail -f <logfile>`, Ctrl-C to exit.

If enabled using `CONTAINER_REMOVE_ENABLED` in `config.sh`, the script removes
all Docker containers on the host prior to creating a new one. Removal fails if
any containers are running. To successfully run the script to completion in this
case, please stop all running containers manually before running the script
again.

When the processes have had enough time to execute, the application can be
accessed by giving the virtual machine domain name to a web browser and
connecting. The backend container serves the built frontend to connecting
clients.

## When the application should be brought down, execute stop script

TODO implement stop script

## Host management cheatsheet
Check computation resource usage:<br>
`top`<br>
use 'q' to exit.

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
`kill <process ID>`
or the more forceful:<br>
`kill -9 <process ID>`

Check command documentation:<br>
`man <command>`<br>
To search in man pages, press '/' and give a search term. Cycle through matches
using 'n' and 'N'.<br>
`<command> --help`
