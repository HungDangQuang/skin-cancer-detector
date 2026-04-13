# Skin Cancer Detector

Deep learning-based skin cancer classification using dermoscopy images (HAM10000/ISIC dataset).

## Classes

| Code | Description |
|---|---|
| `mel` | Melanoma |
| `nv` | Melanocytic nevi |
| `bcc` | Basal cell carcinoma |
| `akiec` | Actinic keratoses / Intraepithelial carcinoma |
| `bkl` | Benign keratosis |
| `df` | Dermatofibroma |
| `vasc` | Vascular lesions |

## Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS

# Install dependencies
make install-dev

# Configure environment
cp .env.example .env
# Edit .env with your paths
```

## Usage

```bash
# 1. Prepare data (download HAM10000 to data/raw/ first)
make prepare

# 2. Train with default config
make train

# 3. Train with specific model
make train-efficientnet

# 4. Evaluate on test set
make evaluate

# 5. Run tests
make test
```

## Project Structure

```
skin-cancer-detector/
├── configs/          # Hydra YAML configs (hyperparameters, model, data)
├── data/             # Raw, processed data and split CSVs
├── src/              # Source code (importable package)
│   ├── data/         # Dataset, DataModule, transforms
│   ├── models/       # Architecture definitions and registry
│   ├── training/     # Trainer, losses, optimizers, callbacks
│   ├── evaluation/   # Metrics, confusion matrix, Grad-CAM
│   ├── inference/    # Predictor and ensemble
│   └── utils/        # Seed, logger, config, checkpoint helpers
├── scripts/          # CLI entry points
├── notebooks/        # EDA and result analysis notebooks
├── reports/          # Thesis figures and final metrics
└── tests/            # Unit tests
```

## Experiment Tracking

Experiments are tracked with MLflow locally:
```bash
mlflow ui --backend-store-uri experiments/runs
```

## Citation

HAM10000 Dataset:
> Tschandl, P., Rosendahl, C. & Kittler, H. The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions. Sci. Data 5, 180161 (2018).
