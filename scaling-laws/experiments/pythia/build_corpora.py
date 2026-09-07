"""Build the two fixed, size-matched eval/entropy corpora for the alpha_N sweep.

Corpora (Pythia's GPT-NeoX byte-level BPE tokenizer, id-identical across the
Pythia suite):
  - prose: wikitext-103-raw train prefix
  - code:  codeparrot/github-code shard 00000 prefix (Python code)

Saves per corpus:
  - {prose,code}_tokens.npy   : first ENT_MAX=50M tokens (int32)
  - {prose,code}_eval.npy     : first EVAL=4M tokens (int32)

Usage: python build_corpora.py
"""
import os
import time

import numpy as np
import pandas as pd
from transformers import AutoTokenizer

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'corpora')
ENT_MAX = 50_000_000
EVAL = 4_000_000

WT_RAW = [
    '/home/ciods/Shahul/research/scaling-laws/data/wt103raw_train-00000-of-00002.parquet',
    '/home/ciods/Shahul/research/scaling-laws/data/wt103raw_train-00001-of-00002.parquet',
]
CODE_SHARD = 'codeparrot/github-code'
CODE_FILE = 'data/train-00000-of-01126.parquet'


def tokenize_stream(name, iter_texts, tokenizer, max_tokens):
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    ids = []
    total = 0
    n_chunks = 0
    for texts in iter_texts:
        enc = tokenizer(texts, add_special_tokens=False)
        for e in enc['input_ids']:
            ids.append(e)
            total += len(e)
            if total >= max_tokens:
                # keep only up to max_tokens
                flat = np.concatenate([np.array(a, dtype=np.int32) for a in ids])
                flat = flat[:max_tokens]
                np.save(os.path.join(OUT, f'{name}_tokens.npy'), flat)
                np.save(os.path.join(OUT, f'{name}_eval.npy'), flat[:EVAL])
                print(f'{name}: {total:,} tokens in {time.time()-t0:.0f}s '
                      f'({n_chunks} chunks); saved tokens + eval slice')
                return
        n_chunks += 1
        if n_chunks % 10 == 0:
            print(f'{name}: {total:,} tokens so far ({time.time()-t0:.0f}s)')
    flat = np.concatenate([np.array(a, dtype=np.int32) for a in ids])
    flat = flat[:max_tokens]
    np.save(os.path.join(OUT, f'{name}_tokens.npy'), flat)
    np.save(os.path.join(OUT, f'{name}_eval.npy'), flat[:EVAL])
    print(f'{name}: {total:,} tokens in {time.time()-t0:.0f}s; saved')


def main():
    # NOTE: Pythia's tokenizer (GPT-NeoX) is NOT id-identical to the stock
    # 'gpt2' tokenizer: different vocab layout and merges. Must use Pythia's.
    tokenizer = AutoTokenizer.from_pretrained('EleutherAI/pythia-70m')

    def wt_chunks(chunk=4000):
        for path in WT_RAW:
            col = pd.read_parquet(path, columns=['text'])['text'].tolist()
            for i in range(0, len(col), chunk):
                yield col[i:i + chunk]

    if not os.path.exists(os.path.join(OUT, 'prose_tokens.npy')):
        tokenize_stream('prose', wt_chunks(), tokenizer, ENT_MAX)

    from huggingface_hub import hf_hub_download
    local = hf_hub_download(CODE_SHARD, CODE_FILE, repo_type='dataset')
    print('code shard downloaded to', local)

    def code_chunks(chunk=4000):
        col = pd.read_parquet(local, columns=['content'])['content'].fillna('').tolist()
        for i in range(0, len(col), chunk):
            yield col[i:i + chunk]

    tokenize_stream('code', code_chunks(), tokenizer, ENT_MAX)
    os.remove(local)
    print('removed code shard cache; done')


if __name__ == '__main__':
    main()
