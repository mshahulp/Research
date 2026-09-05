#!/bin/bash
# P39 single-domain control: run matrix (sequential on one GPU).
cd /home/ciods/Shahul/research/scaling-laws
OUT=results/raw/p39
mkdir -p $OUT
for d in 64 128 256 384; do
  for dom in prose code; do
    for s in 0 1; do
      echo "[$(date +%H:%M:%S)] start d=$d dom=$dom seed=$s"
      ./.venv/bin/python experiments/prediction_validation/train_p39.py \
        --domain $dom --d $d --budget 12000 --seed $s --out $OUT
    done
  done
done
echo "[$(date +%H:%M:%S)] ALL DONE"
