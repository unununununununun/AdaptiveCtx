from __future__ import annotations
import os
from sqlalchemy import Column, Integer, String, LargeBinary, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///data.db")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

Base: declarative_base = declarative_base(cls=AsyncAttrs)

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True)
    ns = Column(String(64), index=True, nullable=False, default="global")
    text = Column(Text, nullable=False)
    embedding = Column(LargeBinary, nullable=False)
    meta = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # helper conversions -----------------------------------------------------------------
    @staticmethod
    def emb_to_bytes(arr):
        import numpy as np
        return np.asarray(arr, dtype="float32").tobytes()

    @staticmethod
    def bytes_to_emb(b):
        import numpy as np
        return np.frombuffer(b, dtype="float32")

# -----------------------------------------------------------------------------
# Training queue: fresh Q/A pairs awaiting fine-tune
# -----------------------------------------------------------------------------


class TrainSample(Base):
    __tablename__ = "train_queue"

    id = Column(Integer, primary_key=True)
    ns = Column(String(64), index=True)
    text = Column(Text, nullable=False)
    used = Column(Integer, default=0)  # 0 = not yet in training, 1 = consumed
    created_at = Column(DateTime(timezone=True), server_default=func.now())