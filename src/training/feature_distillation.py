"""
Feature / relational Knowledge Distillation losses for binary classification.

WHY: at K=1 (binary) a single logit carries too little information to distill
richly. Relational KD [Park et al. 2019] instead distills the *structure* of the
penultimate features — the pairwise DISTANCE and the triplet-wise ANGLE among the
samples in a batch. Each side's structure is computed WITHIN its own feature space
and then normalized, so RKD needs NO projector and is immune to a teacher/student
channel-dim mismatch (C_t != C_s). It composes additively with the existing logit
KD loss (BinaryDistillationLoss).

CRITICAL: never compare feat_s to feat_t element-wise (different dims / spaces).
Only their normalized relational matrices are matched.

Memory: the angle term materializes (B, B, C) difference tensors and a (B, B, B)
angle tensor. At batch_size=64 that is a few tens of MB — fine. If OOM on a large
teacher, lower the batch or subsample the angle term.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


def _pdist(feat: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    """
    Pairwise Euclidean distance matrix (B, B) for ``feat`` (B, C).

    Follows Park et al.'s numerically-safe form: clamp the squared distances to a
    small positive ``eps`` BEFORE ``sqrt`` (so the gradient at a zero distance is
    finite, not ``1/(2*0) = inf``), then zero the diagonal after the sqrt. Passing
    a raw ``clamp_min(0).sqrt()`` here would produce NaN gradients on the diagonal.
    """
    sq = feat.pow(2).sum(dim=1)
    prod = feat @ feat.t()
    dist = (sq.unsqueeze(1) + sq.unsqueeze(0) - 2 * prod).clamp_min(eps).sqrt()
    dist = dist.clone()
    idx = torch.arange(feat.size(0), device=feat.device)
    dist[idx, idx] = 0.0
    return dist


class RKDLoss(nn.Module):
    """
    Relational KD [Park et al. 2019]: distance-wise + angle-wise structure matching.

    Args:
        weight_dist:  weight of the distance-wise term (Park 2019 uses 25).
        weight_angle: weight of the angle-wise term    (Park 2019 uses 50).

    forward(feat_s, feat_t) -> scalar:
        feat_s: student features (B, C_s), requires grad.
        feat_t: teacher features (B, C_t), detached (teacher is frozen).
    Distances are mean-normalized per side, so an absolute scale difference between
    the two feature spaces does not matter — only the relational structure does.
    """

    def __init__(self, weight_dist: float = 25.0, weight_angle: float = 50.0):
        super().__init__()
        self.weight_dist = weight_dist
        self.weight_angle = weight_angle

    def forward(self, feat_s: torch.Tensor, feat_t: torch.Tensor) -> torch.Tensor:
        # --- distance-wise: match mean-normalized pairwise-distance matrices ---
        with torch.no_grad():
            dt = _pdist(feat_t)
            pos_t = dt[dt > 0]
            mean_dt = pos_t.mean() if pos_t.numel() > 0 else dt.new_ones(())
            dt = dt / (mean_dt + 1e-12)
        ds = _pdist(feat_s)
        pos_s = ds[ds > 0]
        mean_ds = pos_s.mean() if pos_s.numel() > 0 else ds.new_ones(())
        ds = ds / (mean_ds + 1e-12)
        loss_d = F.smooth_l1_loss(ds, dt)

        # --- angle-wise: match the cosine of every sample triplet ---
        with torch.no_grad():
            td = feat_t.unsqueeze(0) - feat_t.unsqueeze(1)   # (B, B, C_t)
            t_norm = F.normalize(td, p=2, dim=2)
            t_angle = torch.bmm(t_norm, t_norm.transpose(1, 2))  # (B, B, B)
        sd = feat_s.unsqueeze(0) - feat_s.unsqueeze(1)       # (B, B, C_s)
        s_norm = F.normalize(sd, p=2, dim=2)
        s_angle = torch.bmm(s_norm, s_norm.transpose(1, 2))
        loss_a = F.smooth_l1_loss(s_angle, t_angle)

        return self.weight_dist * loss_d + self.weight_angle * loss_a
