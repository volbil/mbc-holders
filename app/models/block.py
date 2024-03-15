from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from datetime import datetime
from .base import Base


class Block(Base):
    __tablename__ = "service_blocks"

    blockhash: Mapped[str] = mapped_column(String(64), index=True)
    transactions: Mapped[list[str]] = mapped_column(ARRAY(String))
    created: Mapped[datetime]
    timestamp: Mapped[int]
    height: Mapped[int]
    prev_blockhash: Mapped[str] = mapped_column(
        String(64), index=True, nullable=True
    )