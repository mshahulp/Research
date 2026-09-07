"""P39 single-domain control (audit E5, scoped).

Test whether the code-vs-prose alpha_N ordering (code faster) survives
single-domain training with everything else matched. Pythia is mixed-domain;
this removes that confound.

Design:
  - Data: prose/code GPT-NeoX 50M-token corpora, remapped to a SHARED
    top-K vocabulary (by combined prose+code frequency) + OOV, so the
    tokenizer is identical across domains (matched-tokenizer control).
  - Model: weight-tied tiny GPT (like experiments/empirical/train.py),
    ctx=256, L=2, d in {64,128,256} (or --sizes), fixed step budget.
  - Eval: same-domain eval slice, mean CE.
  - Boundary fractions recomputed on the remapped space via plug-in
    (smoothed) next-token top-1 mass for a matched reference.

Usage:
  python train_p39.py --domain prose --d 128 --budget 12000 --out ../../../results/raw/p39
  python train_p39.py --boundary-only   # quick plug-in boundary fractions
"""
import argparse
import os
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

HERE = os.path.dirname(os.path.abspath(__file__))
CORP = os.path.join(os.path.dirname(HERE), 'pythia', 'corpora')
V_FULL = 50304
KT = 4096


def load_remap():
    cache = os.path.join(CORP, f'top{KT}_remap.npz')
    if os.path.exists(cache):
        z = np.load(cache)
        return z['top'], z['remap']
    cnt = np.zeros(V_FULL)
    for name in ('prose', 'code'):
        ids = np.load(os.path.join(CORP, f'{name}_tokens.npy'), mmap_mode='r')
        for i in range(0, len(ids), 25_000_000):
            cnt += np.bincount(np.asarray(ids[i:i + 25_000_000]), minlength=V_FULL)
    top = np.argsort(cnt)[::-1][:KT]
    remap = np.full(V_FULL, KT, dtype=np.int32)   # OOV -> KT
    remap[top] = np.arange(KT, dtype=np.int32)
    np.savez(cache, top=top, remap=remap)
    return top, remap


def load_ids(name, remap, which='tokens'):
    ids = np.load(os.path.join(CORP, f'{name}_{which}.npy'))
    return remap[np.asarray(ids)]


class GPT(nn.Module):
    def __init__(self, vocab, d, layers, ctx, heads=4):
        super().__init__()
        self.tok = nn.Embedding(vocab, d)
        self.pos = nn.Embedding(ctx, d)
        self.blocks = nn.ModuleList([_Block(d, heads) for _ in range(layers)])
        self.ln = nn.LayerNorm(d)
        self.head = nn.Linear(d, vocab, bias=False)
        self.tok.weight = self.head.weight
        self.ctx = ctx
        mask = torch.triu(torch.ones(ctx, ctx) * float('-inf'), diagonal=1)
        self.register_buffer('attn_mask', mask)

    def forward(self, x):
        B, T = x.shape
        h = self.tok(x) + self.pos(torch.arange(T, device=x.device))
        for blk in self.blocks:
            h = blk(h, self.attn_mask[:T, :T])
        h = self.ln(h)
        return self.head(h)


class _Block(nn.Module):
    def __init__(self, d, heads):
        super().__init__()
        self.attn = nn.MultiheadAttention(d, heads, batch_first=True)
        self.ln1 = nn.LayerNorm(d)
        self.ff = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))
        self.ln2 = nn.LayerNorm(d)

    def forward(self, x, mask):
        a, _ = self.attn(self.ln1(x), self.ln1(x), self.ln1(x), attn_mask=mask, need_weights=False)
        x = x + a
        x = x + self.ff(self.ln2(x))
        return x


def eval_loss(model, val, batch=32, device='cuda'):
    model.eval()
    vocab = model.head.out_features
    ctx = model.ctx
    x = val[: (val.shape[0] // ctx) * ctx].view(-1, ctx)
    total = cnt = 0.0
    with torch.no_grad():
        for i in range(0, x.shape[0], batch):
            b = x[i:i + batch].to(device)
            logits = model(b)
            loss = F.cross_entropy(logits[:, :-1].reshape(-1, vocab), b[:, 1:].reshape(-1))
            total += loss.item() * b[:, 1:].numel()
            cnt += b[:, 1:].numel()
    model.train()
    return total / cnt


def boundary_fraction(model, val, batch=32, thresh=0.95, device='cuda'):
    model.eval()
    x = val[: (val.shape[0] // model.ctx) * model.ctx].view(-1, model.ctx)
    top_mass = []
    with torch.no_grad():
        for i in range(0, x.shape[0], batch):
            b = x[i:i + batch].to(device)
            p = F.softmax(model(b)[:, :-1].float(), dim=-1)
            top, _ = p.max(dim=-1)
            top_mass.append((top > thresh).float().mean().item())
    model.train()
    return float(np.mean(top_mass))


def train(args, remap, outdir):
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = 'cuda'
    train_ids = load_ids(args.domain, remap, 'tokens')
    val = torch.from_numpy(load_ids(args.domain, remap, 'eval').astype(np.int64))
    V = KT + 1
    ctx = 256
    D = args.D
    train = torch.from_numpy(train_ids[:D].astype(np.int64))
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
            print(f'  [{args.domain} d={args.d} s={args.seed}] step {step}/{steps} '
                  f'train={loss.item():.4f} val={v:.4f} ({time.time()-t0:.0f}s)', flush=True)
    params = sum(p.numel() for p in model.parameters())
    bf = boundary_fraction(model, val)
    os.makedirs(outdir, exist_ok=True)
    name = f'p39_{args.domain}_d{args.d}_L{args.layers}_s{args.seed}'
    np.savez(os.path.join(outdir, name + '.npz'),
             domain=args.domain, d=args.d, layers=args.layers, seed=args.seed,
             D=int(D), params=int(params), vocab=V,
             best_val=float(best_val), best_step=int(best_step),
             final_val=float(eval_loss(model, val)), boundary_fraction=bf)
    print(f'DONE {name}: best_val={best_val:.4f} (step {best_step}), '
          f'params={params/1e6:.2f}M, boundary={bf:.4f}')


def boundary_only(remap):
    """Plug-in boundary fraction: share of positions where smoothed plug-in
    next-token top-1 mass exceeds 0.95 (matched across domains, remapped space)."""
    V = KT + 1
    for name in ('prose', 'code'):
        ids = load_ids(name, remap, 'eval')
        n2 = np.zeros((V, V))
        n2 += np.bincount(ids[:-1] * V + ids[1:], minlength=V * V).reshape(V, V)
        smooth = (n2 + 0.5) / (n2.sum(axis=1, keepdims=True) + 0.5 * V)
        top = smooth.max(axis=1)
        frac = np.sum(n2.sum(axis=1) * (top > 0.95)) / ids.shape[0]
        print(f'{name}: plug-in (add-0.5) boundary fraction (top1>0.95) = {frac:.4f}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--domain', choices=['prose', 'code'])
    ap.add_argument('--d', type=int, default=128)
    ap.add_argument('--layers', type=int, default=2)
    ap.add_argument('--D', type=int, default=50_000_000)
    ap.add_argument('--budget', type=int, default=12000)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--boundary-only', action='store_true')
    ap.add_argument('--out', default=os.path.join(HERE, '..', '..', '..', 'results', 'raw', 'p39'))
    args = ap.parse_args()
    top, remap = load_remap()
    if args.boundary_only:
        boundary_only(remap)
    else:
        train(args, remap, args.out)
