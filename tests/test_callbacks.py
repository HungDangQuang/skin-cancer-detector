import json

import pytest
import torch

from src.training.callbacks import ExtraCheckpoints, ModelCheckpoint


def make_model():
    model = torch.nn.Linear(2, 1)
    return model, torch.optim.SGD(model.parameters(), lr=0.1)


def test_extra_checkpoint_tracks_its_own_best_epoch(tmp_path):
    model, opt = make_model()
    main = ModelCheckpoint(tmp_path / "checkpoints", monitor="pauc_at_tpr80", mode="max", save_last=False)
    extra = ExtraCheckpoints(["auprc"], checkpoint_dir=tmp_path / "checkpoints", run_dir=tmp_path)

    # pAUC peaks at epoch 2, AUPRC at epoch 3 (and ties at 4 — first epoch wins).
    history = [(0.10, 0.20), (0.15, 0.25), (0.12, 0.40), (0.11, 0.40)]
    for epoch, (pauc, auprc) in enumerate(history, start=1):
        metrics = {"pauc_at_tpr80": pauc, "auprc": auprc, "loss": 1.0}
        main.step(pauc, model, opt, epoch, metrics)
        extra.step(metrics, model, opt, epoch)
    extra.save_val_metrics()

    assert torch.load(tmp_path / "checkpoints" / "best_model.pth", weights_only=False)["epoch"] == 2
    assert torch.load(tmp_path / "checkpoints" / "best_model_auprc.pth", weights_only=False)["epoch"] == 3
    saved = json.loads((tmp_path / "val_metrics_auprc.json").read_text())
    assert saved["best_epoch"] == 3 and saved["auprc"] == 0.40
    assert not (tmp_path / "checkpoints" / "last_model.pth").exists()


def test_no_extra_monitors_writes_nothing(tmp_path):
    model, opt = make_model()
    extra = ExtraCheckpoints([], checkpoint_dir=tmp_path / "checkpoints", run_dir=tmp_path)
    extra.step({"auprc": 0.5}, model, opt, 1)
    extra.save_val_metrics()
    assert not (tmp_path / "checkpoints").exists()
    assert not list(tmp_path.glob("val_metrics_*.json"))


def test_unknown_extra_monitor_raises(tmp_path):
    with pytest.raises(ValueError):
        ExtraCheckpoints(["loss"], checkpoint_dir=tmp_path, run_dir=tmp_path)
