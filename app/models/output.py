from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import Numeric
from sqlalchemy import String
from .base import Base


class Output(Base):
    __tablename__ = "service_outputs"

    blockhash: Mapped[str] = mapped_column(String(64), index=True)
    shortcut: Mapped[str] = mapped_column(String(70), index=True)
    address: Mapped[str] = mapped_column(String(70), index=True)
    txid: Mapped[str] = mapped_column(String(64), index=True)
    amount: Mapped[Numeric] = mapped_column(Numeric(28, 8))
    spent: Mapped[bool]
    index: Mapped[int]
