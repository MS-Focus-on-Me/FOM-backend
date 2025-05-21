from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Azure MySQL 서버 정보 넣기
DATABASE_URL = "mysql+mysqlconnector://zoonhyeong:6Team123@fomdb.mysql.database.azure.com:3306/fomdb"

engine = create_engine(DATABASE_URL, echo=True) 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()