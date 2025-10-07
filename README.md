# SmartCanvas
## Usage with Docker

Check out full instructions [HERE](docs/docker.md)

## Prerequisites
* Python 3.12.*
* Poetry (2.1 or higher recommended)
* Node (22 tested)

## Install Python
Check for installation
```
python3 --version
python --version
```

Depending on your OS of choice load and install python from https://www.python.org/downloads/ or via package manager. (Many Linux distros already have python)

**NOTE**
<br>
Up to version **3.12.11** is currently supported. Using newer will mostly likely not work with current dependencies.
<br>
Pyenv is a good option for multiple python versions https://github.com/pyenv/pyenv.

## Install pipx
Follow instructions here -> https://pipx.pypa.io/stable/installation/

## Install poetry 
After python and pipx are installed insall poetru with pipx
```
pipx install poetry
```
After installing reload you shell and poetry should work.



## Backend in the terminal
The backend environment is managed with [Poetry](https://python-poetry.org/), a Python package and project manager. To install the project and its prerequisites simply use

```ps
poetry install
```

For any following commands it is assumed that the created Python virtual environment has been activated in the terminal. Development tools like Visual Studio Code handle venv activation automatically, but in case you need to invoke commands in a fresh terminal you can use `poetry env activate` to get the activation command.

### Running

Move to poetrys virtual env before running the app. https://python-poetry.org/docs/managing-environments/#bash-csh-zsh 
```
eval $(poetry env activate)
```

To run the web backend, you can use.
```ps
flask --app web run
```

And for unit testing, you can simply use the `pytest` command to run the tests defined in [`/tests/`](/tests/).
```ps
pytest
```

## Frontend in the terminal
The frontend is managed with [npm](https://nodejs.org/en) and can be installed in the [`smartcanvas-frontend`](/smartcanvas-frontend/) directory with
```ps
npm install
```
and started with
```
npm run dev
```

Before deploying, the frontend can be built into a static bundle in the [`web/static`](/web/static) folder with 
```
npm run build
```

## Other considerations
The project comes with a VSCode [`launch.json`](/.vscode/launch.json) to simplify debugging the backend and frontend separately. When contributing, strongly consider utilizing tooling like VSCode to simplify the environment management, and to [run strict type checks](vscode://settings/python.analysis.typeCheckingMode) on your code.

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
- @pklemettila
- @JokelaR
- @Petercode12
- @naanatin
- @juvalta
- @sanpitka 
