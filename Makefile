.PHONY: install install-dev prepare train evaluate test lint format clean

install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install

prepare:
	python scripts/prepare_data.py

train:
	python scripts/train.py

train-efficientnet:
	python scripts/train.py model=efficientnet_b3

train-resnet:
	python scripts/train.py model=resnet50

evaluate:
	python scripts/evaluate.py

predict:
	python scripts/predict.py

tune:
	python scripts/tune_hyperparams.py

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	flake8 src/ scripts/ tests/
	isort --check-only src/ scripts/ tests/
	black --check src/ scripts/ tests/

format:
	isort src/ scripts/ tests/
	black src/ scripts/ tests/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
