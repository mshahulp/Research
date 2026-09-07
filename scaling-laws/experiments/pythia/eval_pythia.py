"""Evaluate the Pythia ladder on the two fixed eval corpora.

Per model in [70m,160m,410m,1b,1.4b,2.8b] and corpus in [prose, code]:
  - per-window (1024-token, no overlap) mean next-token cross-entropy in bits
    on the FIXED 4M-token eval slice; saved to window_losses/{model}_{corpus}.npy
  - overall mean + empirical SE
Reference boundary measurement (Pythia-410m only): fraction of token positions
with reference top-1 next-token probability > 0.95 (pre-registered premise).

Usage: python eval_pythia.py
"""
import json
import os
import time

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'corpora')
WL = os.path.join(HERE, 'window_losses')
os.makedirs(WL, exist_ok=True)
LN2 = np.log(2.0)
SEQ = 1024
SIZES = ['70m', '160m', '410m', '1b', '1.4b', '2.8b']
REF = '410m'


def window_losses(model, ids, device):
    model.eval()
    n = (len(ids) // SEQ) * SEQ
    x = torch.from_numpy(ids[:n].astype(np.int64)).to(device).view(-1, SEQ)
    wl = []
    with torch.no_grad():
        for i in range(0, x.shape[0], 2):
            b = x[i:i + 2]
            logits = model(b).logits[:, :-1]
            loss = F.cross_entropy(
                logits.reshape(-1, logits.shape[-1]), b[:, 1:].reshape(-1),
                reduction='mean')
            wl.append(loss.item() / LN2)
    return np.array(wl)


def boundary_fraction(model, ids, device, thresh=0.95):
    model.eval()
    n = (len(ids) // SEQ) * SEQ
    x = torch.from_numpy(ids[:n].astype(np.int64)).to(device).view(-1, SEQ)
    frac = []
    with torch.no_grad():
        for i in range(0, x.shape[0], 2):
            b = x[i:i + 2]
            logits = model(b).logits[:, :-1]
            p = F.softmax(logits.float(), dim=-1)
            top, _ = p.max(dim=-1)
            frac.append((top > thresh).float().mean().item())
    return np.mean(frac)


def main():
    device = 'cuda'
    results = {'sizes': SIZES, 'boundary_ref': REF, 'threshold': 0.95,
               'corpora': {}, 'params': {}}
    for s in SIZES:
        t0 = time.time()
        model = AutoModelForCausalLM.from_pretrained(
            f'EleutherAI/pythia-{s}', torch_dtype=torch.float16).to(device)
        params = sum(p.numel() for p in model.parameters())
        results['params'][s] = int(params)
        print(f'pythia-{s}: {params:,} params (load {time.time()-t0:.0f}s)', flush=True)
        for name in ['prose', 'code']:
            ids = np.load(os.path.join(OUT, f'{name}_eval.npy'))
            wl = window_losses(model, ids, device)
            np.save(os.path.join(WL, f'{s}_{name}.npy'), wl)
            m, se = wl.mean(), wl.std() / np.sqrt(len(wl))
            results['corpora'].setdefault(name, {})[s] = {'mean': float(m), 'se': float(se)}
            print(f'  {name}: loss={m:.4f} +/- {se:.5f} bits/token '
                  f'({len(wl)} windows, {time.time()-t0:.0f}s)', flush=True)
        del model
        torch.cuda.empty_cache()

    t0 = time.time()
    ref = AutoModelForCausalLM.from_pretrained(
        f'EleutherAI/pythia-{REF}', torch_dtype=torch.float16).to(device)
    for name in ['prose', 'code']:
        ids = np.load(os.path.join(OUT, f'{name}_eval.npy'))
        f = boundary_fraction(ref, ids, device)
        results['corpora'][name]['boundary_fraction'] = f
        print(f'  boundary fraction ({REF}, >0.95) {name}: {f:.4f} '
              f'({time.time()-t0:.0f}s)', flush=True)
    with open(os.path.join(HERE, 'eval_results.json'), 'w') as fh:
        json.dump(results, fh, indent=2)
    print('DONE eval_pythia')


if __name__ == '__main__':
    main()
