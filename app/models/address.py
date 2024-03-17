from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import Numeric
from sqlalchemy import String
from .base import Base


class Address(Base):
    __tablename__ = "service_addresses"

    address: Mapped[str] = mapped_column(String(70), index=True, unique=True)
    balance: Mapped[Numeric] = mapped_column(Numeric(28, 8))
