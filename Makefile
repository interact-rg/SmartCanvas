VENV = venv
PACKAGE = smart_canvas
INT_PATH = bin
ifeq ($(OS), Windows_NT)
	INT_PATH = scripts
endif
PYTHON = $(VENV)/$(INT_PATH)/python
PIP = $(VENV)/$(INT_PATH)/pip

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
	export FLASK_APP=web; $(PYTHON) -m flask run

.PHONY: web-local
web-local: init
	gunicorn --worker-class eventlet -w 1 'web:create_app()'

.PHONY: hl
hl: init
	heroku local

.PHONY: test
test: init
	$(PYTHON) -m pytest tests --disable-pytest-warnings

.PHONY: test-w-warnings
test-w-warnings: init
	$(PYTHON) -m pytest tests

.PHONY: test-cov
test-cov: init
	$(PYTHON) -m pytest --cov=$(PACKAGE) --cov-report=term-missing -v

.PHONY: lint
lint: init
	$(PYTHON) -m pylint $(PACKAGE) tests

.PHONY: clean
clean:
	rm -rf ./**/__pycache__ ./**/**/__pycache__
	rm -rf $(VENV)
