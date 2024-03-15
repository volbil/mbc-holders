from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import String
from .base import Base


class Input(Base):
    __tablename__ = "service_inputs"

    blockhash: Mapped[str] = mapped_column(String(64), index=True)
    shortcut: Mapped[str] = mapped_column(String(70), index=True)
    txid: Mapped[str] = mapped_column(String(64), index=True)
    index: Mapped[int]
