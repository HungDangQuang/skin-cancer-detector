.PHONY: install install-dev prepare train-teacher train-student-b0 train-student-mobilenet train-student-mobilevit poc-teacher poc-student poc-all evaluate test lint format clean

install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install

prepare:
	python scripts/prepare_data.py

# Step 1: Train teacher
train-teacher:
	python scripts/train_teacher.py

# Step 2: Train each student via KD
train-student-b0:
	python scripts/train_student.py student=efficientnet_b0

train-student-mobilenet:
	python scripts/train_student.py student=mobilenetv3_large

train-student-mobilevit:
	python scripts/train_student.py student=mobilevit_s

# Train all students sequentially
train-all-students: train-student-b0 train-student-mobilenet train-student-mobilevit

# POC (Proof-of-Concept) — smoke test the whole pipeline with 2 epochs.
poc-teacher:
	python scripts/train_teacher.py --config-name config_poc

poc-student:
	python scripts/train_student.py --config-name config_poc student=efficientnet_b0

poc-all: poc-teacher poc-student

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
