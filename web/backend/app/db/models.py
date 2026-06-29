from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    benutzername = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    erstellt_am = Column(DateTime, default=datetime.utcnow)
    aktiv = Column(Boolean, default=True)

    charaktere = relationship("Charakter", back_populates="user", cascade="all, delete-orphan")


class Charakter(Base):
    __tablename__ = "charaktere"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    char_name = Column(String, nullable=False, default="")
    active_setting_name = Column(String, nullable=False, default="SWAE")
    char_gen_completed = Column(Boolean, default=False)
    charakter_daten = Column(JSON, nullable=False)
    erstellt_am = Column(DateTime, default=datetime.utcnow)
    aktualisiert_am = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="charaktere")

    __table_args__ = (
        UniqueConstraint("user_id", "char_name", name="uq_user_char_name"),
    )
