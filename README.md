# SmartCanvas
## Usage with Docker

Check out full instructions [HERE](docs/docker.md)

## Prerequisites
* Python 3.12.*
* Poetry (2.1 or higher recommended)
* Node (22 tested)

## Backend in the terminal
The backend environment is managed with [Poetry](https://python-poetry.org/), a Python package and project manager. To install the project and its prerequisites simply use

```ps
poetry install
```

For any following commands it is assumed that the created Python virtual environment has been activated in the terminal. Development tools like Visual Studio Code handle venv activation automatically, but in case you need to invoke commands in a fresh terminal you can use `poetry env activate` to get the activation command.

### Running
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

## Issues with GDPR

Smartcanvas is not currently GDPR compliant.

As per the legislation (https://gdpr-info.eu/art-4-gdpr/), personal data includes the face of the person and doing image manipulation with your face is processing (adaptation or alteration) personal data. This means that the user will need to accept GDPR, even if we don’t save their face. It would seem that even temporarily storing the face in RAM wouldn’t be GDPR compliant, as we would still be processing personal information. The app deletes (as of 3.5.25) the faces/altered faces of people after the QR code countdown has passed, so no information *should* be saved.

Consent needs to be a “clear affirmative action”, and in the past Smartcanvas asked for a thumbs up to accept GDPR. However, what constitutes a “thumbs up” was defined by programming logic and affected by camera quality and thus cannot be guaranteed to be robust enough for legal consent.

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
