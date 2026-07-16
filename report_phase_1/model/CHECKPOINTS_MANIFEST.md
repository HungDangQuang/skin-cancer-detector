# Checkpoint manifest (Phase 1)

Checkpoint goc o `experiments/runs/`; report chi symlink fold_0 (dai dien) de khoi nhan ban 9.1 GB.

**efficientformerv2_s2** (model vua test on-device): `.pth` chua tai ve Mac (chi o cluster) nen
folder `student_kd/kd_convnextv2_base_to_efficientformerv2_s2/` chua **file `.pte` da benchmark**
(47 MB) thay cho symlink `.pth`. Muon ban `.pth` goc thi rsync tu:
`keg@slurm.uit.edu.vn:.../kd_convnextv2_base_to_efficientformerv2_s2/fold_0/checkpoints/best_model.pth`

| Category | Run | Fold | Size | Path |
|---|---|---|---|---|
| student_kd | kd_convnextv2_base_to_fastvit_sa12 | fold_0 | 121M | `experiments/runs/kd_convnextv2_base_to_fastvit_sa12/fold_0/checkpoints/best_model.pth` |
| student_kd | kd_convnextv2_base_to_fastvit_sa12 | fold_1 | 121M | `experiments/runs/kd_convnextv2_base_to_fastvit_sa12/fold_1/checkpoints/best_model.pth` |
| student_kd | kd_convnextv2_base_to_fastvit_sa12 | fold_2 | 121M | `experiments/runs/kd_convnextv2_base_to_fastvit_sa12/fold_2/checkpoints/best_model.pth` |
| student_kd | kd_convnextv2_base_to_fastvit_sa12 | fold_3 | 121M | `experiments/runs/kd_convnextv2_base_to_fastvit_sa12/fold_3/checkpoints/best_model.pth` |
| student_kd | kd_convnextv2_base_to_fastvit_sa12 | fold_4 | 121M | `experiments/runs/kd_convnextv2_base_to_fastvit_sa12/fold_4/checkpoints/best_model.pth` |
| student_kd | kd_convnextv2_base_to_mobilenetv4_conv_medium | fold_0 | 97M | `experiments/runs/kd_convnextv2_base_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth` |
| student_kd | kd_convnextv2_base_to_mobilenetv4_conv_medium | fold_1 | 97M | `experiments/runs/kd_convnextv2_base_to_mobilenetv4_conv_medium/fold_1/checkpoints/best_model.pth` |
| student_kd | kd_convnextv2_base_to_mobilenetv4_conv_medium | fold_2 | 97M | `experiments/runs/kd_convnextv2_base_to_mobilenetv4_conv_medium/fold_2/checkpoints/best_model.pth` |
| student_kd | kd_convnextv2_base_to_mobilenetv4_conv_medium | fold_3 | 97M | `experiments/runs/kd_convnextv2_base_to_mobilenetv4_conv_medium/fold_3/checkpoints/best_model.pth` |
| student_kd | kd_convnextv2_base_to_mobilenetv4_conv_medium | fold_4 | 97M | `experiments/runs/kd_convnextv2_base_to_mobilenetv4_conv_medium/fold_4/checkpoints/best_model.pth` |
| student_kd | kd_efficientnet_b4_to_mobilenetv3_large |  | 48M | `experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/checkpoints/best_model.pth` |
| student_kd | kd_efficientnet_b4_to_mobilenetv3_large | fold_0 | 48M | `experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/fold_0/checkpoints/best_model.pth` |
| student_kd | kd_efficientnet_b4_to_mobilenetv3_large | fold_1 | 48M | `experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/fold_1/checkpoints/best_model.pth` |
| student_kd | kd_efficientnet_b4_to_mobilenetv3_large | fold_2 | 48M | `experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/fold_2/checkpoints/best_model.pth` |
| student_kd | kd_efficientnet_b4_to_mobilenetv3_large | fold_3 | 48M | `experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/fold_3/checkpoints/best_model.pth` |
| student_kd | kd_efficientnet_b4_to_mobilenetv3_large | fold_4 | 48M | `experiments/runs/kd_efficientnet_b4_to_mobilenetv3_large/fold_4/checkpoints/best_model.pth` |
| student_kd | kd_efficientnetv2_m_to_fastvit_sa12 | fold_0 | 121M | `experiments/runs/kd_efficientnetv2_m_to_fastvit_sa12/fold_0/checkpoints/best_model.pth` |
| student_kd | kd_efficientnetv2_m_to_fastvit_sa12 | fold_1 | 121M | `experiments/runs/kd_efficientnetv2_m_to_fastvit_sa12/fold_1/checkpoints/best_model.pth` |
| student_kd | kd_efficientnetv2_m_to_fastvit_sa12 | fold_2 | 121M | `experiments/runs/kd_efficientnetv2_m_to_fastvit_sa12/fold_2/checkpoints/best_model.pth` |
| student_kd | kd_efficientnetv2_m_to_fastvit_sa12 | fold_3 | 121M | `experiments/runs/kd_efficientnetv2_m_to_fastvit_sa12/fold_3/checkpoints/best_model.pth` |
| student_kd | kd_efficientnetv2_m_to_fastvit_sa12 | fold_4 | 121M | `experiments/runs/kd_efficientnetv2_m_to_fastvit_sa12/fold_4/checkpoints/best_model.pth` |
| student_kd | kd_efficientnetv2_m_to_mobilenetv4_conv_medium | fold_0 | 97M | `experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_0/checkpoints/best_model.pth` |
| student_kd | kd_efficientnetv2_m_to_mobilenetv4_conv_medium | fold_1 | 97M | `experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_1/checkpoints/best_model.pth` |
| student_kd | kd_efficientnetv2_m_to_mobilenetv4_conv_medium | fold_2 | 97M | `experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_2/checkpoints/best_model.pth` |
| student_kd | kd_efficientnetv2_m_to_mobilenetv4_conv_medium | fold_3 | 97M | `experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_3/checkpoints/best_model.pth` |
| student_kd | kd_efficientnetv2_m_to_mobilenetv4_conv_medium | fold_4 | 97M | `experiments/runs/kd_efficientnetv2_m_to_mobilenetv4_conv_medium/fold_4/checkpoints/best_model.pth` |
| teacher | maxvit_base | fold_0 | 1.3G | `experiments/runs/teacher/maxvit_base/fold_0/checkpoints/best_model.pth` |
| teacher | maxvit_base | fold_1 | 1.3G | `experiments/runs/teacher/maxvit_base/fold_1/checkpoints/best_model.pth` |
| teacher | maxvit_base | fold_2 | 1.3G | `experiments/runs/teacher/maxvit_base/fold_2/checkpoints/best_model.pth` |
| teacher | maxvit_base | fold_3 | 1.3G | `experiments/runs/teacher/maxvit_base/fold_3/checkpoints/best_model.pth` |
| teacher | maxvit_base | fold_4 | 1.3G | `experiments/runs/teacher/maxvit_base/fold_4/checkpoints/best_model.pth` |
