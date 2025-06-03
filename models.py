from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text, BLOB
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reference_text = Column(String(255))

class Diary(Base):
    __tablename__ = 'diary'
    diary_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    emotion_score = Column(Integer)
    summary = Column(Text)
    photo = Column(BLOB)
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TempDiary(Base):
    __tablename__ = 'temp_diary'
    temp_diary_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    title = Column(String(255))
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Emotion(Base):
    __tablename__ = 'emotions'
    emotion_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    diary_id = Column(Integer, ForeignKey('diary.diary_id'), nullable=False)
    joy = Column(Integer, default=0)
    sadness = Column(Integer, default=0)
    anger = Column(Integer, default=0)
    fear = Column(Integer, default=0)
    disgust = Column(Integer, default=0)
    anxiety = Column(Integer, default=0)
    envy = Column(Integer, default=0)
    bewilderment = Column(Integer, default=0)
    boredom = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())