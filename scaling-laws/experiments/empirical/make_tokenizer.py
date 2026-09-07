"""Train a small BPE tokenizer (vocab 1024) on wikitext-103-raw and tokenize.

1024 is chosen so that n-gram packing of up to 6 tokens fits int64
(1024^6 = 2^60). Saves tokens.npy (int32) and the tokenizer.

Usage: python make_tokenizer.py
"""
import os
import numpy as np
from tokenizers import Tokenizer, models, trainers, pre_tokenizers

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data', 'wiki.train.raw')
OUT = os.path.join(HERE, 'stats')
os.makedirs(OUT, exist_ok=True)

def _read_chunks(f, size):
    while True:
        buf = f.read(size)
        if not buf:
            break
        yield [buf]

tok = Tokenizer(models.BPE())
tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=True)
trainer = trainers.BpeTrainer(vocab_size=1024, special_tokens=[], min_frequency=2)
print('training BPE (vocab 1024) on first 120M chars...')
with open(DATA, encoding='utf-8') as f:
    tok.train_from_iterator(_read_chunks(f, 5_000_000), trainer=trainer, length=120_000_000)
print('vocab size:', tok.get_vocab_size())

print('tokenizing full train set...')
toks = []
with open(DATA, encoding='utf-8') as f:
    for chunk in _read_chunks(f, 20_000_000):
        enc = tok.encode_batch(chunk, add_special_tokens=False)
        for e in enc:
            toks.append(np.asarray(e.ids, dtype=np.int32))
ids = np.concatenate(toks)
print('token count:', len(ids))
np.save(os.path.join(OUT, 'tokens.npy'), ids)
tok.save(os.path.join(OUT, 'bpe1024.json'))
print('saved tokens.npy and bpe1024.json')
