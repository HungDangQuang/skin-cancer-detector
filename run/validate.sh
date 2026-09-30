#!/usr/bin/env bash
# ============================================================================
# Static pipeline validation inside the REAL server venv — §1 import sanity and
# §2 Hydra dry-load for every registered model. CPU-only, ~1 min.
#
# This is the runtime half of the validate-pipeline checks: the Mac can only do
# AST/compose-level checks, this actually imports torch/timm and builds every
# model in MODEL_REGISTRY, so a broken registry/config merge fails here in
# seconds instead of 6 hours into a training run.
#
# Usage:
#   bash run/validate.sh
#   bash run/validate.sh GPU=cpu     # (default anyway — no GPU is touched)
#
# Exit 0 = pipeline composes and every model builds.
# ============================================================================
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
for arg in "$@"; do export "${arg?}"; done

start_log "validate"
activate_venv
# CPU-only: model construction never needs CUDA, and forcing CPU keeps this
# runnable while a training job owns the GPU.
export CUDA_VISIBLE_DEVICES=""

echo "[run] §1 import sanity"
python -c "
import src.data
import src.models
import src.training
import src.evaluation
import src.utils
from src.models.registry import MODEL_REGISTRY, build_model_from_name
print('imports ok |', len(MODEL_REGISTRY), 'models registered')
"

echo "[run] §2 Hydra dry-load (reproduces the scripts/evaluate.py path for every registered model)"
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

echo "[run] DONE"
