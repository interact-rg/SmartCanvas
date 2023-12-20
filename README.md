# SmartCanvas
## Usage with Docker

Check out full instructions [HERE](docs/docker.md)

## Usage with terminal commands
If you do not have Make installed use the following commands on a terminal (like Git Bash) to install and run the program.
```
git clone https://github.com/interact-rg/SmartCanvas.git
cd SmartCanvas
pip install .
python -m smart_canvas
```

You can also add extra options such as `--fullscreen` for fullscreen mode or `--camera 1` to change the camera source.


## Usage with Make
Makefile is used to manage the build scripts.\
On Windows cmd or Powershell is not supported.\
To run `make` commands on Windows, use BASH emulator (for e.g. git bash) or alternatively WSL.

Init environment:  
`make init`

Run the program:  
`make run`

Run the web-service:  
`make web`

Run the web-service with gunicorn:\
`make web-local`

Test the code:  
`make test`

Test the code with warnings:  
`make test-w-warnings`

Test the code with coverage:  
`make test-cov`

Lint the code:  
`make lint`

Clean environment:  
`make clean`

## Accessing web app (if running)

[SmartCanvas web app running on cPouta service](http://86.50.228.113:5000/)

Check out further info [HERE](docs/web_app_usage.md)

## Contributing

See the [CONTRIBUTING.md](CONTRIBUTING.md) guide.

## Contributors
- @Vilatsut
- @loppastoffa
- @hpeteri
- @juusosar
- @topoto123
- @vtiinanen
- @jarkkokotaniemi
- @jvuorine
- @jruntti20
- @Mikroudz
- @Redha-Aouadja
- @hengzhang-pro
- @antilaanssi
- @MeaNoCulpa
- @0LTSU0
- @jouniwho
- @morriskrr
