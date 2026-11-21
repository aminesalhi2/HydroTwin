# HydroTwin Makefile
# For Unix / Git Bash / WSL environments
PYTHON = .venv/Scripts/python
STREAMLIT = .venv/Scripts/streamlit
PYTEST = .venv/Scripts/pytest

.PHONY: help setup data train eval app test demo

help:
	@echo "HydroTwin commands:"
	@echo "  make setup   - Install dependencies and setup environment"
	@echo "  make data    - Generate synthetic scenarios and demand dataset"
	@echo "  make train   - Train forecasting and leak localization models"
	@echo "  make eval    - Evaluate on unseen scenarios and generate docs/EVALUATION.md"
	@echo "  make app     - Launch the Streamlit dashboard"
	@echo "  make test    - Run pytest test suite"
	@echo "  make demo    - Regenerate precomputed demo cache and verify demo readiness"

setup:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) generate_assumptions.py

data:
	$(PYTHON) run.py data

train:
	$(PYTHON) run.py train

eval:
	$(PYTHON) run.py eval

app:
	$(STREAMLIT) run app/main.py

test:
	$(PYTEST) tests/ -v

demo:
	$(PYTHON) run.py demo
