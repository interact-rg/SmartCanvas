SHELL:=/bin/bash
VENV = venv
PACKAGE = smart_canvas
INT_PATH = bin/python3.9
ifeq ($(OS), Windows_NT)
	INT_PATH = scripts
endif
PYTHON = $(VENV)/$(INT_PATH)/python
PIP = $(VENV)/$(INT_PATH)/pip
TOKEN = $(shell $(PYTHON) -c 'import uuid; print(uuid.uuid1())')

$(VENV)/$(INT_PATH)/activate:
	python -m venv venv
	$(PIP) install .

.PHONY: init
init: $(VENV)/$(INT_PATH)/activate

.PHONY: run
run: init
	$(PYTHON) -m $(PACKAGE)

.PHONY: web
web: init
	export FLASK_APP=web; \
	export CLIENT_TOKEN=$(TOKEN); \
	$(PYTHON) -V
	$(PYTHON) -m flask run

.PHONY: web-local
web-local: init
	export CLIENT_TOKEN=$(TOKEN); \
	gunicorn --worker-class eventlet -w 1 'web:create_app()'

.PHONY: hl
hl: init
	export CLIENT_TOKEN=$(TOKEN); \
	heroku local

.PHONY: test
test: init
	$(PYTHON) -m pytest tests --disable-pytest-warnings

.PHONY: test-w-warnings
test-w-warnings: init
	$(PYTHON) -m pytest tests

.PHONY: test-cov
test-cov: init
	$(PYTHON) -m pytest --cov=$(PACKAGE) --cov="web" --cov-report=term-missing -v

.PHONY: lint
lint: init
	$(PYTHON) -m pylint $(PACKAGE) tests web

.PHONY: clean
clean:
	rm -rf ./**/__pycache__ ./**/**/__pycache__
	rm -rf $(VENV)
