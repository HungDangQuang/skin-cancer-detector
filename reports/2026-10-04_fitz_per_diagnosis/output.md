## (1) Độ nhạy theo chẩn đoán tại ngưỡng app — P0, Fitzpatrick17k-C

| Chẩn đoán | n ác (fold 4) | sáng · trung bình · tối | Độ nhạy fold 4 [Wilson 95%] | Độ nhạy cộng 5 fold (mỗi fold ngưỡng pad_sens90 riêng — điểm vận hành khác nhau) |
|---|---|---|---|---|
| basal cell carcinoma | 404 | 210 · 167 · 27 | 0.678 [0.631; 0.722] | 0.801 |
| squamous cell carcinoma | 348 | 200 · 122 · 26 | 0.664 [0.613; 0.711] | 0.796 |
| melanoma | 167 | 86 · 53 · 28 | 0.539 [0.463; 0.613] | 0.630 |
| mycosis fungoides | 137 | 67 · 56 · 14 | 0.299 [0.229; 0.381] | 0.491 |
| actinic keratosis | 136 | 89 · 39 · 8 | 0.360 [0.284; 0.444] | 0.546 |
| superficial spreading melanoma ssm | 104 | 82 · 17 · 5 | 0.500 [0.406; 0.594] | 0.525 |
| kaposi sarcoma | 96 | 34 · 45 · 17 | 0.323 [0.238; 0.422] | 0.479 |
| malignant melanoma | 87 | 63 · 21 · 3 | 0.586 [0.481; 0.684] | 0.577 |
| lentigo maligna | 58 | 28 · 28 · 2 | 0.466 [0.343; 0.592] | 0.555 |
| basal cell carcinoma morpheiform | 46 | 43 · 3 · 0 | 0.717 [0.575; 0.827] | 0.852 |
| solid cystic basal cell carcinoma | 40 | 32 · 8 · 0 | 0.775 [0.625; 0.877] | 0.875 |

## (2) AUC từng chẩn đoán so với toàn bộ ảnh lành (không phụ thuộc ngưỡng), trung bình 5 fold

| Chẩn đoán | AUC student P0 | AUC teacher efficientnetv2_m | AUC teacher convnextv2_base |
|---|---|---|---|
| basal cell carcinoma | 0.792 | 0.761 | 0.783 |
| squamous cell carcinoma | 0.784 | 0.767 | 0.779 |
| melanoma | 0.665 | 0.641 | 0.697 |
| mycosis fungoides | 0.581 | 0.541 | 0.602 |
| actinic keratosis | 0.611 | 0.624 | 0.623 |
| superficial spreading melanoma ssm | 0.602 | 0.569 | 0.667 |
| kaposi sarcoma | 0.586 | 0.590 | 0.590 |
| malignant melanoma | 0.653 | 0.633 | 0.653 |
| lentigo maligna | 0.603 | 0.616 | 0.657 |
| basal cell carcinoma morpheiform | 0.832 | 0.824 | 0.868 |
| solid cystic basal cell carcinoma | 0.839 | 0.833 | 0.864 |

## (3) III-b của P0 (fold 4) khi bỏ một số chẩn đoán khỏi nhóm ác — CHỈ CHẨN ĐOÁN, không phải cổng

| Bỏ khỏi nhóm ác | Độ nhạy sáng · trung bình · tối [Wilson 95%] | n ác còn lại |
|---|---|---|
| không bỏ (III-b hiện hành) | 0.603 [0.571; 0.634] · 0.503 [0.461; 0.544] · 0.508 [0.423; 0.592] | 934 · 559 · 130 |
| actinic keratosis | 0.624 [0.591; 0.656] · 0.521 [0.478; 0.564] · 0.516 [0.429; 0.603] | 845 · 520 · 122 |
| mycosis fungoides + kaposi sarcoma | 0.633 [0.599; 0.665] · 0.557 [0.511; 0.602] · 0.566 [0.467; 0.659] | 833 · 458 · 99 |
| cả ba | 0.660 [0.625; 0.693] · 0.585 [0.537; 0.631] · 0.582 [0.480; 0.678] | 744 · 419 · 91 |
