from sqlalchemy import BigInteger, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM
from datetime import datetime


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Staff(Base):
    __tablename__ = 'staff'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    patronymic: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(ENUM('male', 'female', 'unknown', name='gender'),
                                        nullable=False,
                                        default='unknown')

    def __repr__(self):
        return f'<Staff {self.last_name} {self.first_name}>'
