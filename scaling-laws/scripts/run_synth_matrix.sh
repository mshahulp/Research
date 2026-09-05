#!/bin/bash
# Synthetic sanity-check matrix: 2 regimes x 3 sizes x 2 seeds = 12 runs.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
LOG=results/raw/synth_matrix.log
mkdir -p results/raw/synth
echo "[$(date +%H:%M:%S)] START synthetic matrix" | tee "$LOG"
for regime in A B; do
  for d in 128 256 384; do
    for s in 0 1; do
      echo "[$(date +%H:%M:%S)] start regime=$regime d=$d seed=$s" | tee -a "$LOG"
      $PY scripts/synth_train.py --regime "$regime" --d "$d" --seed "$s" >> "$LOG" 2>&1
    done
  done
done
echo "[$(date +%H:%M:%S)] ALL DONE" | tee -a "$LOG"
