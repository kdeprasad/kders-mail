from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
try:
    from pgvector.sqlalchemy import Vector
except Exception:
    # if pgvector is not installed in dev environment, fallback placeholder
    Vector = None
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    full_name = Column(String(256), nullable=True)
    is_teacher = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="owner")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(512), nullable=True)
    body = Column(Text, nullable=False)
    sender = Column(String(256), nullable=False)
    recipient = Column(String(256), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # optional vector embedding for RAG (pgvector)
    if Vector is not None:
        embedding = Column(Vector(384), nullable=True)
    mail_raw = Column(Text, nullable=True)

    owner = relationship("User", back_populates="messages")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class GroupMember(Base):
    __tablename__ = "group_members"
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

class AICache(Base):
    __tablename__ = "ai_cache"
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(512), nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
