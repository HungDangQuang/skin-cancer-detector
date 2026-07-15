.PHONY: install install-dev prepare prepare-poc train-teacher train-student-mobilenetv4 train-student-fastvit train-student-efficientformer poc-teacher poc-student poc-all evaluate test lint format clean

install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install

prepare:
	python scripts/prepare_data.py

# POC fixtures — synthetic data so you don't need ISIC 2024.
prepare-poc:
	python scripts/prepare_poc_data.py

# Step 1: Train teacher
train-teacher:
	python scripts/train_teacher.py

# Step 2: Train each student via KD
train-student-mobilenetv4:
	python scripts/train_student.py student=mobilenetv4_conv_medium

train-student-fastvit:
	python scripts/train_student.py student=fastvit_sa12

train-student-efficientformer:
	python scripts/train_student.py student=efficientformerv2_s2

# Train all students sequentially
train-all-students: train-student-mobilenetv4 train-student-fastvit train-student-efficientformer

# POC (Proof-of-Concept) — smoke test the whole pipeline with 2 epochs.
poc-teacher:
	python scripts/train_teacher.py --config-name config_poc

poc-student:
	python scripts/train_student.py --config-name config_poc student=mobilenetv4_conv_medium

poc-all: prepare-poc poc-teacher poc-student

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
