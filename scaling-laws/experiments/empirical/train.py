"""Train a small GPT (character- or token-level) on wikitext-103-raw.

Measures the validation cross-entropy (bits/unit) of a transformer trained on
exactly D units, for a given model size. Used for the alpha_N and alpha_D
sweeps of the empirical validation.

Usage:
  python train.py --data tok --d 128 --layers 2 --ctx 256 --D 8000000 --seed 0 --out runs
  python train.py --data char --d 128 --layers 4 --ctx 256 --D 60000000 --seed 0 --out runs
"""
import argparse
import math
import os
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

HERE = os.path.dirname(os.path.abspath(__file__))
STATS = os.path.join(HERE, 'stats')


def load_data(kind):
    if kind == 'tok':
        ids = np.load(os.path.join(STATS, 'tokens.npy'))
        vocab = 1024
    else:
        ids = np.load(os.path.join(STATS, 'char_ids.npy'))
        vocab = 257
    return torch.from_numpy(ids.astype(np.int64)), vocab


class GPT(nn.Module):
    def __init__(self, vocab, d, layers, ctx, heads=4):
        super().__init__()
        self.tok = nn.Embedding(vocab, d)
        self.pos = nn.Embedding(ctx, d)
        self.blocks = nn.ModuleList([Block(d, heads) for _ in range(layers)])
        self.ln = nn.LayerNorm(d)
        self.head = nn.Linear(d, vocab, bias=False)
        self.tok.weight = self.head.weight  # weight tying
        self.ctx = ctx
        # causal mask: position t attends only to positions <= t
        mask = torch.triu(torch.ones(ctx, ctx) * float('-inf'), diagonal=1)
        self.register_buffer('attn_mask', mask)

    def forward(self, x):
        B, T = x.shape
        h = self.tok(x) + self.pos(torch.arange(T, device=x.device))
        for blk in self.blocks:
            h = blk(h, self.attn_mask[:T, :T])
        h = self.ln(h)
        return self.head(h)


class Block(nn.Module):
    def __init__(self, d, heads):
        super().__init__()
        self.attn = nn.MultiheadAttention(d, heads, batch_first=True)
        self.ln1 = nn.LayerNorm(d)
        self.ff = nn.Sequential(
            nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))
        self.ln2 = nn.LayerNorm(d)

    def forward(self, x, mask):
        a, _ = self.attn(self.ln1(x), self.ln1(x), self.ln1(x),
                         attn_mask=mask, need_weights=False)
        x = x + a
        x = x + self.ff(self.ln2(x))
        return x


def run(args):
    ids, vocab = load_data(args.data)
    N = len(ids)
    if args.data == 'tok':
        ctx = 256
    else:
        ctx = args.ctx
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    # train split: first D units; val split: official wikitext validation set
    D = min(args.D, N - 4_000_000)
    train = ids[:D]
    vf = os.path.join(STATS, 'val_tokens.npy')
    if args.data == 'tok' and os.path.exists(vf):
        val = torch.from_numpy(np.load(vf).astype(np.int64))
        print(f'val: official wikitext split ({len(val):,} tokens)')
    else:
        val = ids[N - 4_000_000:N]

    batch = args.batch
    steps = D // (batch * ctx)
    if args.steps:
        steps = args.steps
    steps = max(steps, 100)

    model = GPT(vocab, args.d, args.layers, ctx).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=steps, eta_min=args.lr * 0.05)

    def eval_loss():
        model.eval()
        with torch.no_grad():
            x = val[: (val.shape[0] // ctx) * ctx].view(-1, ctx)
            total = 0.0
            cnt = 0
            for i in range(0, x.shape[0], batch):
                b = x[i:i + batch].to(device)
                logits = model(b)
                # predict next token: positions 0..T-2 -> targets 1..T-1
                loss = F.cross_entropy(
                    logits[:, :-1].reshape(-1, vocab), b[:, 1:].reshape(-1))
                total += loss.item() * b[:, 1:].numel()
                cnt += b[:, 1:].numel()
        model.train()
        return total / cnt

    t0 = time.time()
    best_val, best_step = 1e9, 0
    for step in range(1, steps + 1):
        i = ((step - 1) * batch * ctx) % max(D, 1)
        i = min(i, D - batch * ctx)
        x = train[i:i + batch * ctx].view(batch, ctx).to(device)
        logits = model(x)
        loss = F.cross_entropy(
            logits[:, :-1].reshape(-1, vocab), x[:, 1:].reshape(-1))
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        sched.step()
        if step % 250 == 0 or step == steps:
            v = eval_loss()
            if v < best_val:
                best_val, best_step = v, step
            print(f'  step {step}/{steps} train={loss.item():.4f} val={v:.4f} '
                  f'({(step * batch * ctx / 1e6):.1f}M units seen, {time.time()-t0:.0f}s)',
                  flush=True)

    # final eval
    vf = eval_loss()
    params = sum(p.numel() for p in model.parameters())
    result = dict(
        data=args.data, d=args.d, layers=args.layers, ctx=ctx,
        D=int(D), params=int(params), seed=args.seed,
        best_val=best_val, best_step=int(best_step),
        final_val=vf, last_train=float(loss.item()),
        units=('tokens' if args.data == 'tok' else 'chars'),
    )
    os.makedirs(args.out, exist_ok=True)
    name = f"{args.data}_d{args.d}_L{args.layers}_D{int(D)}_s{args.seed}"
    np.savez(os.path.join(args.out, name + '.npz'), **result)
    print(f'DONE {name}: best_val={best_val:.4f} (step {best_step}), '
          f'final_val={vf:.4f}, params={params/1e6:.2f}M', flush=True)
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--data', choices=['tok', 'char'], required=True)
    p.add_argument('--d', type=int, default=128)
    p.add_argument('--layers', type=int, default=2)
    p.add_argument('--ctx', type=int, default=256)
    p.add_argument('--D', type=int, required=True)
    p.add_argument('--steps', type=int, default=0,
                   help='fixed training-step budget (0 = one epoch of D)')
    p.add_argument('--batch', type=int, default=32)
    p.add_argument('--lr', type=float, default=3e-4)
    p.add_argument('--seed', type=int, default=0)
    p.add_argument('--out', default='runs')
    run(p.parse_args())
