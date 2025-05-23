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

# class Diary(Base):
#     __tablename__ = 'diary'
#     diary_id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
#     emotion_score = Column(Integer)
#     summary = Column(Text)
#     photo = Column(BLOB)
#     content = Column(Text)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())

# class TempDiary(Base):
#     __tablename__ = 'temp_diary'
#     temp_diary_id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
#     title = Column(String(255))
#     content = Column(Text)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())