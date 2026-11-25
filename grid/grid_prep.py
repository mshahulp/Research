"""Step 1. Build BPE-1024 tokens for WikiText-103-raw (train + validation) and bytes-per-token for the validation set.
Run once:  python grid_prep.py            (needs: pip install datasets tokenizers numpy)
Outputs in ./data: train.npy, val.npy (uint16), bpe1024.json, meta.json (val_bytes, val_tokens)."""
import os, json, numpy as np
from datasets import load_dataset
from tokenizers import Tokenizer, models, trainers, pre_tokenizers
os.makedirs("data", exist_ok=True)
ds = load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1")
train_txt = "".join(ds["train"]["text"]); val_txt = "".join(ds["validation"]["text"])
tok = Tokenizer(models.BPE()); tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=True)
tr = trainers.BpeTrainer(vocab_size=1024, special_tokens=[], min_frequency=2)
tok.train_from_iterator([train_txt[i:i+5_000_000] for i in range(0, min(len(train_txt), 120_000_000), 5_000_000)], trainer=tr)
def enc(txt, step=20_000_000):
    out = []
    for i in range(0, len(txt), step):
        out.append(np.asarray(tok.encode(txt[i:i+step], add_special_tokens=False).ids, dtype=np.uint16))
    return np.concatenate(out)
tr_ids, va_ids = enc(train_txt), enc(val_txt)
np.save("data/train.npy", tr_ids); np.save("data/val.npy", va_ids); tok.save("data/bpe1024.json")
meta = dict(train_tokens=int(len(tr_ids)), val_tokens=int(len(va_ids)), val_bytes=len(val_txt.encode("utf-8")))
json.dump(meta, open("data/meta.json", "w")); print(meta)
