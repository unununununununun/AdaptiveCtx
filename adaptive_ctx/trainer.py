"""Simple LoRA fine-tune stub.

Usage:
    python -m adaptive_ctx.trainer --ns global --batch 128

For now it just pops N samples from train_queue and prints them.
"""

import asyncio, argparse
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
    print(f"Fetched {len(batch)} samples for ns='{args.ns}'. (Stub trainer)\n")
    for row in batch[:5]:
        print("•", row.text[:80].replace("\n", "  ") + ("…" if len(row.text) > 80 else ""))
    # TODO: integrate LoRA fine-tune here

if __name__ == "__main__":
    asyncio.run(main())