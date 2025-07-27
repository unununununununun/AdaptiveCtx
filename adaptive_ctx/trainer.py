"""Simple LoRA fine-tune stub.

Usage:
    python -m adaptive_ctx.trainer --ns global --batch 128

For now it just pops N samples from train_queue and prints them.
"""

import asyncio, argparse, os, time, datetime, uuid, tempfile, shutil
from pathlib import Path

import torch
from sentence_transformers import SentenceTransformer, losses, InputExample

from .db import async_session, TrainSample
from sqlalchemy import select, update

async def fetch_batch(ns: str, batch_size: int = 128):
    async with async_session() as ses:
        result = await ses.execute(
            select(TrainSample).where(TrainSample.used == 0, TrainSample.ns == ns).limit(batch_size)
        )
        rows = result.scalars().all()
        # mark as used
        if rows:
            await ses.execute(update(TrainSample).where(TrainSample.id.in_([r.id for r in rows])).values(used=1))
            await ses.commit()
        return rows

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ns", default="global")
    ap.add_argument("--batch", type=int, default=128)
    args = ap.parse_args()
    batch = await fetch_batch(args.ns, args.batch)
    if not batch:
        print("No fresh samples in train_queue – nothing to train.")
        return

    print(f"Training on {len(batch)} samples …")

    # --- build dataset (simple positive pairs Q,A) ---------------------------
    examples = []
    for row in batch:
        if "Q:" in row.text and "A:" in row.text:
            parts = row.text.split("\n", 1)
            q = parts[0].replace("Q:", "").strip()
            a = parts[1].replace("A:", "").strip() if len(parts) > 1 else ""
            examples.append(InputExample(texts=[q, a]))

    if len(examples) < 2:
        print("Not enough Q/A formatted samples, skipping.")
        return

    model_name = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")
    model = SentenceTransformer(model_name)

    # Use MultipleNegativesRankingLoss (common for sentence embeddings)
    train_loss = losses.MultipleNegativesRankingLoss(model)

    loader = torch.utils.data.DataLoader(examples, batch_size=16, shuffle=True)

    model.fit(
        train_objectives=[(loader, train_loss)],
        epochs=1,
        show_progress_bar=True,
        warmup_steps=10,
        output_path=None,
    )

    ckpt_dir = Path("checkpoints") / datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    model.save(str(ckpt_dir))
    print(f"Saved fine-tuned model to {ckpt_dir}")
    # print instruction for reload
    print("Call POST /admin/reload_encoder {\"path\": \"" + str(ckpt_dir) + "\"} to activate.")

if __name__ == "__main__":
    asyncio.run(main())