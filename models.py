from sqlalchemy import CheckConstraint, BigInteger, String, Date
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


class Person(Base):
    __tablename__ = 'person'
    __table_args__ = (
        CheckConstraint("department BETWEEN 1 AND 4", name="check_department"),
        CheckConstraint("room BETWEEN 1 AND 10", name="check_room"),
        CheckConstraint("date_of_birth BETWEEN DATE '1900-01-01' AND CURRENT_DATE",
                        name='check_date_of_birth_range'))

    id: Mapped[int] = mapped_column(primary_key=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    patronymic: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[datetime] = mapped_column(Date(), nullable=False)
    department: Mapped[int] = mapped_column(nullable=False)
    room: Mapped[int] = mapped_column(nullable=False)

    def __repr__(self):
        return f'<Person {self.last_name} {self.first_name}'
