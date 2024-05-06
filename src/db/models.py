from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = ()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class Lead(Base):
    __tablename__ = "lead"

    # Crm id
    id = Column(BigInteger, primary_key=True)
    pipeline = Column(String(256))
    status = Column(String(256))
    name = Column(String(256))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    created_by = Column(DateTime)
    updated_by = Column(DateTime)
    contact = Column(String(256))
    sale = Column(BigInteger)
    date = Column(DateTime)
    speciality = Column(String(256))
    work_type = Column(String(256))
    koef = Column(Float)
    pages = Column(Text)
    thema = Column(Text)
    uniqueness = Column(Text)
    real_deadline = Column(DateTime)
    deadline_for_author = Column(DateTime)
    files = Column(String(256))
    fix_time = Column(BigInteger)
    author_name = Column(String(256))
    author_id = Column(String(256))
    expenses = Column(BigInteger)
    expenses_status = Column(BigInteger)
    expenses_multy = Column(BigInteger)
    note = Column(Text)
    team_lead = Column(BigInteger)
    priority = Column(BigInteger, default=0)
    alert_comment = Column(Text)
    sec_author = Column(String(256))
    alert = Column(BigInteger)
    sec_price = Column(BigInteger)
    sity = Column(BigInteger)
    university = Column(String(256))
    faculty = Column(BigInteger)
    review = Column(String(256))
    costs_sum = Column(BigInteger)
    correction_count = Column(BigInteger)
    delivery_date = Column(BigInteger)
    shtraf = Column(BigInteger)
    date_done = Column(BigInteger)
    plan = Column(String(256))
    task_current = Column(String(256))
    date_current = Column(BigInteger)
    hotovo = Column(String(256))
    redone_date = Column(BigInteger)
    ready_date = Column(DateTime, nullable=True, default=None)


class Speciality(Base):
    __tablename__ = "speciality"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(256))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Admin(Base):
    __tablename__ = "admin"

    id = Column(BigInteger, primary_key=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    authors = relationship("Author", back_populates="admin", lazy="selectin")


class Author(Base):
    __tablename__ = "author"

    # Telegram id
    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, nullable=True)
    custom_id = Column(BigInteger, nullable=True)
    name = Column(String(256), nullable=True)
    rating = Column(Integer, nullable=True)
    admin_id = Column(BigInteger, ForeignKey("admin.id"), index=True, nullable=True)
    plane_busyness = Column(Float, nullable=True)
    busyness = Column(Float, nullable=True)
    open_leads = Column(Integer, nullable=True)
    auction = Column(Boolean, default=False)
    card_number = Column(String(256), nullable=True)
    telegram_url = Column(String(256), nullable=True)
    specialities = Column(Text, nullable=True)

    is_registered = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    admin = relationship("Admin", back_populates="authors", lazy="selectin")
