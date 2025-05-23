from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # 현재 디렉토리의 .env 파일 읽기

DATABASE_URL = os.getenv('DATABASE_URL', os.environ.get('DATABASE_URL'))
engine = create_engine(DATABASE_URL, pool_recycle=500)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 깃허브를 private으로 하고 하드코딩