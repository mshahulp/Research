"""Step 2. Train the N x D grid. Resumable: finished (size, D, seed) rows in the CSV are skipped.
  python grid_train.py --smoke                    # 2-minute sanity check, run this first
  python grid_train.py --preset light --out results/grid.csv
  python grid_train.py --preset full  --out results/grid.csv
  python grid_train.py --convergence --out results/convergence.csv   # does 2x more training change the loss?
Loss is validation cross-entropy in bits per token, also converted to bits per byte (val_bpb)."""
import argparse, csv, json, math, os, time
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F

SIZES = {"S1": (64, 2, 2, 3e-3), "S2": (128, 2, 4, 2e-3), "S3": (192, 4, 4, 1.5e-3),
         "S4": (256, 6, 8, 1e-3), "S5": (384, 8, 8, 7e-4), "S6": (512, 8, 8, 5e-4)}
PRESETS = {"smoke": dict(sizes=["S1", "S2"], D=[1e6], seeds=[0]),
           "light": dict(sizes=["S1", "S2", "S3", "S4"], D=[1e6, 3e6, 1e7, 3e7], seeds=[0, 1]),
           "full":  dict(sizes=["S1", "S2", "S3", "S4", "S5", "S6"], D=[1e6, 3e6, 1e7, 3e7, 1e8, 2e8], seeds=[0, 1, 2])}
CTX, BATCH, VOCAB = 256, 32, 1024

class Block(nn.Module):
    def __init__(s, d, h):
        super().__init__(); s.h = h; s.ln1 = nn.LayerNorm(d); s.qkv = nn.Linear(d, 3 * d); s.proj = nn.Linear(d, d)
        s.ln2 = nn.LayerNorm(d); s.ff = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(), nn.Linear(4 * d, d))
    def forward(s, x):
        B, T, C = x.shape; q, k, v = s.qkv(s.ln1(x)).view(B, T, 3, s.h, C // s.h).permute(2, 0, 3, 1, 4)
        a = F.scaled_dot_product_attention(q, k, v, is_causal=True).transpose(1, 2).reshape(B, T, C)
        x = x + s.proj(a); return x + s.ff(s.ln2(x))
class GPT(nn.Module):
    def __init__(s, d, L, h):
        super().__init__(); s.tok = nn.Embedding(VOCAB, d); s.pos = nn.Embedding(CTX, d)
        s.blocks = nn.ModuleList([Block(d, h) for _ in range(L)]); s.ln = nn.LayerNorm(d)
        s.head = nn.Linear(d, VOCAB, bias=False); s.head.weight = s.tok.weight
        s.apply(s._init)
    def _init(s, m):
        if isinstance(m, (nn.Linear, nn.Embedding)): nn.init.normal_(m.weight, std=0.02)
        if isinstance(m, nn.Linear) and m.bias is not None: nn.init.zeros_(m.bias)
    def forward(s, x):
        h = s.tok(x) + s.pos(torch.arange(x.shape[1], device=x.device))
        for b in s.blocks: h = b(h)
        return s.head(s.ln(h))
    def n_nonemb(s): return sum(p.numel() for b in s.blocks for p in b.parameters())

@torch.no_grad()
def evaluate(model, ids, dev, amp, max_tokens=2_000_000):
    model.eval(); n = (min(len(ids), max_tokens) // CTX) * CTX; x = ids[:n].view(-1, CTX); tot = 0.0; cnt = 0
    for i in range(0, x.shape[0], 64):
        xb = x[i:i + 64].to(dev)
        with torch.autocast(dev, dtype=amp, enabled=amp is not None):
            lg = model(xb[:, :-1])
        tot += F.cross_entropy(lg.float().reshape(-1, VOCAB), xb[:, 1:].reshape(-1), reduction="sum").item(); cnt += xb[:, 1:].numel()
    model.train(); return tot / cnt / math.log(2)

def run_one(size, D, seed, train_all, val, meta, dev, amp, epochs, min_tok, max_tok, n_evals=20):
    d, L, h, lr = SIZES[size]; torch.manual_seed(seed); np.random.seed(seed)
    model = GPT(d, L, h).to(dev); N = model.n_nonemb(); D = int(D); train = train_all[:D]
    S = int(min(max(epochs * D, min_tok), max_tok)); steps = max(S // (BATCH * CTX), 200); warm = min(200, steps // 10)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, betas=(0.9, 0.95), weight_decay=0.1)
    sched = lambda t: lr * (t + 1) / warm if t < warm else lr * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * (t - warm) / max(1, steps - warm))))
    scaler = torch.cuda.amp.GradScaler(enabled=(dev == "cuda" and amp == torch.float16))
    t0 = time.time(); best, best_step, last_train = 1e9, 0, float("nan"); ev_every = max(steps // n_evals, 1)
    maxstart = D - CTX - 1
    for t in range(steps):
        for g in opt.param_groups: g["lr"] = sched(t)
        st = np.random.randint(0, maxstart, size=BATCH); xb = torch.stack([train[s:s + CTX + 1] for s in st]).to(dev)
        with torch.autocast(dev, dtype=amp, enabled=amp is not None):
            lg = model(xb[:, :-1])
        loss = F.cross_entropy(lg.float().reshape(-1, VOCAB), xb[:, 1:].reshape(-1))
        opt.zero_grad(set_to_none=True); scaler.scale(loss).backward(); scaler.unscale_(opt)
        nn.utils.clip_grad_norm_(model.parameters(), 1.0); scaler.step(opt); scaler.update(); last_train = loss.item() / math.log(2)
        if (t + 1) % ev_every == 0 or t == steps - 1:
            v = evaluate(model, val, dev, amp)
            if v < best: best, best_step = v, t + 1
    last = evaluate(model, val, dev, amp)
    bpt = meta["val_tokens"] / meta["val_bytes"]  # tokens per byte on the full validation set
    return dict(size=size, d=d, layers=L, N=N, D=D, seed=seed, tokens_seen=steps * BATCH * CTX, steps=steps,
                best_val_bits_tok=best, last_val_bits_tok=last, val_bpb=best * bpt, best_step=best_step,
                train_bits_tok_last=last_train, seconds=round(time.time() - t0, 1))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preset", default="light", choices=list(PRESETS)); ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--convergence", action="store_true"); ap.add_argument("--out", default="results/grid.csv")
    ap.add_argument("--epochs", type=float, default=4.0); ap.add_argument("--min_tokens", type=float, default=2e7)
    ap.add_argument("--max_tokens", type=float, default=3e8)
    ap.add_argument("--n_evals", type=int, default=20); ap.add_argument("--sizes", default=None); ap.add_argument("--Ds", default=None); ap.add_argument("--seeds", default=None); a = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    amp = (torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16) if dev == "cuda" else None
    meta = json.load(open("data/meta.json")); tr = torch.from_numpy(np.load("data/train.npy").astype(np.int64))
    va = torch.from_numpy(np.load("data/val.npy").astype(np.int64))
    if a.smoke: a.preset, a.min_tokens, a.max_tokens, a.out = "smoke", 2e6, 2e6, "results/smoke.csv"
    cfg = dict(PRESETS[a.preset])
    if a.sizes: cfg["sizes"] = a.sizes.split(",")
    if a.Ds: cfg["D"] = [float(x) for x in a.Ds.split(",")]
    if a.seeds: cfg["seeds"] = [int(x) for x in a.seeds.split(",")]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    jobs = [(s, D, sd, a.epochs) for s in cfg["sizes"] for D in cfg["D"] for sd in cfg["seeds"]]
    if a.convergence:   # same cell with 1x and 2x the training budget, for the middle size and D
        jobs = [("S3", 1e7, 0, a.epochs), ("S3", 1e7, 0, 2 * a.epochs)]
    done = set()
    if os.path.exists(a.out):
        for r in csv.DictReader(open(a.out)): done.add((r["size"], int(float(r["D"])), int(r["seed"]), float(r.get("epochs", a.epochs))))
    for (s, D, sd, ep) in jobs:
        if (s, int(D), sd, ep) in done: continue
        r = run_one(s, D, sd, tr, va, meta, dev, amp, ep, a.min_tokens, a.max_tokens, n_evals=a.n_evals); r["epochs"] = ep
        new = not os.path.exists(a.out)
        with open(a.out, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(r.keys())); (w.writeheader() if new else None); w.writerow(r)
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
main()
