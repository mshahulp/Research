#!/bin/bash
# alpha_D sweep, fixed model (d=128, 2 layers), token level, wikitext-103-raw.
# Fixed step budget S=12000 per D (best_val reported = early-stopped at the
# data-resolution limit); small D are heavily overtrained (correct), large D
# saturate the model capacity floor (~4.21 bits/token).
cd /home/ciods/Shahul/research/scaling-laws/experiments/empirical
V=/home/ciods/Shahul/research/scaling-laws/.venv/bin/python
for D in 250000 500000 1000000 2000000 4000000 8000000; do
  $V train.py --data tok --d 128 --layers 2 --ctx 256 --D $D --steps 12000 --batch 64 --lr 1e-3 --seed 0 --out runs
done
echo ALL_DONE_ALPHA_D
