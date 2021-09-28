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

init: $(VENV)/$(INT_PATH)/activate

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