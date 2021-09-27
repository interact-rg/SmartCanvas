VENV = venv
PACKAGE = smart_canvas
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

$(VENV)/bin/activate:
	python3 -m venv venv
	$(PIP) install . --use-feature=in-tree-build

init: $(VENV)/bin/activate

run: init
	$(PYTHON) -m $(PACKAGE)

test: init
	$(PYTHON) -m pytest tests

test-cov: init
	$(PYTHON) -m pytest --cov=$(PACKAGE) --cov-report=term-missing -v

lint: init
	$(PYTHON) -m pylint $(PACKAGE) tests

clean:
	rm -rf ./**/__pycache__
	rm -rf $(VENV)

.PHONY: run clean test init
