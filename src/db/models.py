from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Table, func
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


authors_specialties = Table(
    "authors_specialties",
    Base.metadata,
    Column("author_id", BigInteger, ForeignKey("author.id")),
    Column("speciality_id", BigInteger, ForeignKey("speciality.id")),
)


class Lead(Base):
    __tablename__ = "lead"

    # Crm id
    id = Column(BigInteger, primary_key=True)
    status_id = Column(BigInteger, ForeignKey("lead_status.id"), index=True)
    author_id = Column(BigInteger, ForeignKey("author.id"), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    status = relationship("LeadStatus", back_populates="leads")
    author = relationship("Author", back_populates="leads")


class LeadStatus(Base):
    __tablename__ = "lead_status"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(256))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    leads = relationship("Lead", back_populates="status")


class Speciality(Base):
    __tablename__ = "speciality"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(256))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    authors = relationship("Author", secondary=authors_specialties, back_populates="specialities")


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
    full_name = Column(String(256))
    contact = Column(String(256))
    raiting = Column(Float)
    busyness = Column(Float)
    plane_busyness = Column(Float)
    card_number = Column(String(256), nullable=True)
    crm_id = Column(BigInteger, nullable=True, index=True)
    admin_id = Column(BigInteger, ForeignKey("admin.id"), index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    specialities = relationship("Speciality", secondary=authors_specialties, back_populates="authors")
    leads = relationship("Lead", back_populates="author")
    admin = relationship("Admin", back_populates="authors")
