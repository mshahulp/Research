"""Train tiny GPTs on the synthetic corpora (step 10).

Reuses the p39 GPT architecture; reads the synthetic token streams directly
(vocab=128, no remap). Sizes d in {128,256,384}, L=2, ctx=256, fixed budget,
fp16 autocast.

Usage:
  python scripts/synth_train.py --regime A --d 128 --seed 0
  bash scripts/run_synth_matrix.sh   # all 12 runs serially
"""
import argparse
import json
import os
import sys
import time

import numpy as np
import torch
import torch.nn.functional as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'experiments', 'prediction_validation'))
from train_p39 import GPT, eval_loss  # noqa: E402

CORP = os.path.join(ROOT, 'experiments', 'synthetic', 'corpora')
CFG = os.path.join(ROOT, 'experiments', 'synthetic', 'config.json')
V = 128


def train(args, cfg):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = 'cuda'
    train_ids = np.load(os.path.join(CORP, f'{args.regime}_tokens.npy'))
    val = torch.from_numpy(np.load(os.path.join(CORP, f'{args.regime}_eval.npy')).astype(np.int64))
    ctx = 256
    D = len(train_ids)
    train = torch.from_numpy(train_ids.astype(np.int64))
    steps = D // (32 * ctx)
    if args.budget:
        steps = args.budget

    model = GPT(V, args.d, args.layers, ctx).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=steps, eta_min=3e-5)

    t0 = time.time()
    best_val, best_step = 1e9, 0
    for step in range(1, steps + 1):
        i = ((step - 1) * 32 * ctx) % D
        i = min(i, D - 32 * ctx)
        x = train[i:i + 32 * ctx].view(32, ctx).to(device)
        with torch.autocast('cuda', dtype=torch.float16):
            logits = model(x)
            loss = F.cross_entropy(logits[:, :-1].reshape(-1, V), x[:, 1:].reshape(-1))
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        if step % 1000 == 0 or step == steps:
            v = eval_loss(model, val)
            if v < best_val:
                best_val, best_step = v, step
            print(f'  [synth {args.regime} d={args.d} s={args.seed}] step {step}/{steps} '
                  f'train={loss.item():.4f} val={v:.4f} ({time.time()-t0:.0f}s)', flush=True)
    params = sum(p.numel() for p in model.parameters())
    os.makedirs(args.out, exist_ok=True)
    name = f'synth_{args.regime}_d{args.d}_L{args.layers}_s{args.seed}'
    np.savez(os.path.join(args.out, name + '.npz'),
             regime=args.regime, d=args.d, layers=args.layers, seed=args.seed,
             D=int(D), params=int(params), vocab=V,
             best_val=float(best_val), best_step=int(best_step),
             final_val=float(eval_loss(model, val)),
             entropy_floor=float(cfg[args.regime]['entropy_floor']))
    print(f'DONE {name}: best_val={best_val:.4f} (step {best_step}), params={params/1e6:.2f}M, '
          f'E_floor={cfg[args.regime]["entropy_floor"]:.4f}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--regime', choices=['A', 'B'])
    ap.add_argument('--d', type=int, default=128)
    ap.add_argument('--layers', type=int, default=2)
    ap.add_argument('--budget', type=int, default=12000)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', default=os.path.join(ROOT, 'results', 'raw', 'synth'))
    args = ap.parse_args()
    cfg = json.load(open(CFG))
    train(args, cfg)
