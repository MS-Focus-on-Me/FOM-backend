# from sqlalchemy import Column, String, Integer, DateTime
# from sqlalchemy.sql import func
# from database import Base

# class User(Base):
#     __tablename__ = 'users'
#     email = Column(String(255), primary_key=True)
#     name = Column(String(100), nullable=False)
#     password = Column(String(255), nullable=False)
#     created_at = Column(DateTime, server_default=func.now())

# class Diary(Base):
#     __tablename__ = 'diaries'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     user_email = Column(String(255))
#     content = Column(String(500), nullable=False)
#     created_at = Column(DateTime, server_default=func.now())