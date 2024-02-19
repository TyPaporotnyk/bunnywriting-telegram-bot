from sqlalchemy import BigInteger, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
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


class Lead(Base):
    __tablename__ = "lead"

    # Crm id
    id = Column(BigInteger, primary_key=True)

    status_id = Column(BigInteger, ForeignKey("lead_status.id"), index=True)
    author_id = Column(BigInteger, ForeignKey("author.id"), index=True)

    status = relationship("LeadStatus", back_populates="leads")
    author = relationship("Author", back_populates="leads")


class LeadStatus(Base):
    __tablename__ = "lead_status"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(256))

    leads = relationship("Lead", back_populates="status")


class Author(Base):
    __tablename__ = "author"

    # Telegram id
    id = Column(BigInteger, primary_key=True)
    full_name = Column(String(256))

    raiting = Column(Float)
    bussyness = Column(Float)

    card_number = Column(String(256))

    is_admin = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)

    leads = relationship("Lead", back_populates="author")
