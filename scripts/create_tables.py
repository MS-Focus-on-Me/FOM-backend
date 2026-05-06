from database import Base, engine

# 기존 테이블 삭제
import sqlalchemy as sa

with engine.connect() as conn:
    conn.execute(sa.text("DROP TABLE IF EXISTS users"))

# 새 테이블 생성
Base.metadata.create_all(engine)