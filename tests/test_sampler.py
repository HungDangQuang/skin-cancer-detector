import numpy as np
import pytest

from src.data.sampler import DynamicUndersampledSampler


def make_pool():
    """Fold-0-shaped toy pool: a huge ISIC benign pool, a small PAD/DDI one."""
    labels = [0] * 5000 + [1] * 20 + [0] * 40 + [1] * 30 + [0] * 25 + [1] * 10
    sources = ["isic2024"] * 5020 + ["pad_ufes_20"] * 70 + ["ddi"] * 35
    return labels, sources


def historical_draw(labels, ratio, seed, epoch):
    """The pre-2026-09-30 sampler, verbatim — the default must reproduce it."""
    labels = np.array(labels)
    mal = np.where(labels == 1)[0]
    ben = np.where(labels == 0)[0]
    rng = np.random.default_rng(seed + epoch)
    b = rng.choice(ben, size=min(len(mal) * ratio, len(ben)), replace=False)
    return rng.permutation(np.concatenate([mal, b])).tolist()


@pytest.mark.parametrize("with_sources", [False, True])
def test_default_matches_historical_draw(with_sources):
    labels, sources = make_pool()
    s = DynamicUndersampledSampler(labels, ratio=5, seed=42, sources=sources if with_sources else None)
    for epoch in (0, 3):
        s.set_epoch(epoch)
        assert list(s) == historical_draw(labels, 5, 42, epoch)


def test_source_mode_keeps_total_and_fills_minorities():
    labels, sources = make_pool()
    s = DynamicUndersampledSampler(labels, ratio=5, seed=42, sources=sources, stratify_by="source")
    idx = np.array(list(s))
    lab = np.array(labels)[idx]
    src = np.array(sources)[idx]

    assert len(idx) == len(s) == 60 + 5 * 60  # total benign = ratio × all malignant
    assert (lab == 1).sum() == 60  # every malignant, once
    assert len(set(idx.tolist())) == len(idx)  # no duplicates
    # minority sources: min(ratio × n_mal_s, pool) -> whole pool here
    assert ((src == "pad_ufes_20") & (lab == 0)).sum() == 40
    assert ((src == "ddi") & (lab == 0)).sum() == 25
    # the largest pool fills the remainder
    assert ((src == "isic2024") & (lab == 0)).sum() == 300 - 40 - 25


def test_source_mode_caps_minority_at_ratio():
    labels = [0] * 1000 + [1] * 10 + [0] * 100 + [1] * 4
    sources = ["isic2024"] * 1010 + ["pad_ufes_20"] * 104
    s = DynamicUndersampledSampler(labels, ratio=5, seed=0, sources=sources, stratify_by="source")
    idx = np.array(list(s))
    src, lab = np.array(sources)[idx], np.array(labels)[idx]
    assert ((src == "pad_ufes_20") & (lab == 0)).sum() == 20  # 5 × 4, not the whole 100
    assert ((src == "isic2024") & (lab == 0)).sum() == 70 - 20


def test_source_mode_reshuffles_per_epoch_and_is_seeded():
    labels, sources = make_pool()
    a = DynamicUndersampledSampler(labels, sources=sources, stratify_by="source")
    b = DynamicUndersampledSampler(labels, sources=sources, stratify_by="source")
    e0 = list(a)
    a.set_epoch(1)
    assert list(a) != e0
    assert list(b) == e0


def test_invalid_mode_and_missing_sources_raise():
    labels, sources = make_pool()
    with pytest.raises(ValueError):
        DynamicUndersampledSampler(labels, sources=sources, stratify_by="patient")
    with pytest.raises(ValueError):
        DynamicUndersampledSampler(labels, stratify_by="source")
    with pytest.raises(ValueError):
        DynamicUndersampledSampler(labels, sources=sources[:-1])
