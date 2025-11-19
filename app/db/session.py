from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from app.core.config import settings


connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}


engine = create_engine(
    settings.DATABASE_URL,
    pool_size=16,               # 常驻连接池数量(CPU核数 × 2)
    max_overflow=80,            # 当池已满，允许额外开辟的临时连接数(内存 × 2.5)
    pool_timeout=30,           # 等待连接可用的超时（秒）
    pool_recycle=1800,         # 连接回收时间（秒），防止 MySQL “server has gone away”
    pool_pre_ping=True,        # 每次连接前 ping 数据库，自动检测断开连接
    echo=False,                # True 会打印所有 SQL 日志，调试时开启
    future=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
