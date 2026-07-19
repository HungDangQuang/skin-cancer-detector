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
from hydra.core.global_hydra import GlobalHydra
from src.models.registry import MODEL_REGISTRY, build_model_from_name
import os
cfg_dir = os.path.abspath('configs')
# Privileged (LUPI) models need data.metadata_cols to size their tabular branch;
# supply a dummy triple so they build. Plain models ignore these keys.
PRIV_OV = ['data.metadata_as_input=true',
           'data.metadata_cols=[tbp_lv_symm_2axis,tbp_lv_norm_border,tbp_lv_norm_color]']
for root in ['config', 'config_poc']:
    for name in MODEL_REGISTRY:
        priv = name.endswith('_privileged')
        # config_poc's data group (poc.yaml) has no metadata knobs -> skip privileged there.
        if priv and root == 'config_poc':
            print(f'{root:12s} skip {name} (poc data has no metadata knobs)')
            continue
        if GlobalHydra.instance().is_initialized():
            GlobalHydra.instance().clear()
        with initialize_config_dir(version_base=None, config_dir=cfg_dir):
            cfg = compose(config_name=root, overrides=(PRIV_OV if priv else []))
        _, merged = build_model_from_name(name, cfg)
        assert merged.model.name == name, f'{root}/{name}: merge mismatch ({merged.model.name})'
        print(f'{root:12s} ok | built {name}')
"

echo "[job] DONE"
