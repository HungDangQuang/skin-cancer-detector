#!/bin/bash
# ============================================================================
# Static pipeline validation — runs validate-pipeline §1 (imports) and §2
# (Hydra dry-load) inside the real cluster venv. CPU-ONLY (no GPU/MPS).
# Submit:  bash slurm/submit.sh slurm/00_validate.slurm
# Output:  logs/validate_<jobid>.{out,err}
# ============================================================================
#SBATCH --job-name=validate
#SBATCH --output=logs/validate_%j.out
#SBATCH --error=logs/validate_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=2G
#SBATCH --time=00:05:00

source "${SLURM_SUBMIT_DIR:-$(pwd)}/slurm/_lib.sh"
load_python_env

echo "[job] §1 import sanity"
python -c "
import src.data
import src.models
import src.training
import src.evaluation
import src.utils
from src.models.registry import MODEL_REGISTRY, build_model_from_name
from src.training import Trainer, KDTrainer, BinaryDistillationLoss
print('imports ok |', len(MODEL_REGISTRY), 'models registered')
"

echo "[job] §2 Hydra dry-load (reproduces the scripts/evaluate.py path for every registered model)"
python -c "
from hydra import compose, initialize_config_dir
from src.models.registry import MODEL_REGISTRY, build_model_from_name
import os
cfg_dir = os.path.abspath('configs')
for root in ['config', 'config_poc']:
    with initialize_config_dir(version_base=None, config_dir=cfg_dir):
        cfg = compose(config_name=root)
        for name in MODEL_REGISTRY:
            _, merged = build_model_from_name(name, cfg)
            assert merged.model.name == name, f'{root}/{name}: merge mismatch ({merged.model.name})'
            print(f'{root:12s} ok | built {name}')
"

echo "[job] DONE"
