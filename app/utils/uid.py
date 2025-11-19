import hashlib
import os
import random
import time
from sqlalchemy.orm import Session
from app.models import User


def generate_uid(db: Session, datetime: int, secret_salt: str | None = None) -> int:
    secret_salt = secret_salt or os.getenv("SECRET_SALT", "default_salt")

    for attempt in range(100):
        nonce = f"{time.time_ns()}-{random.randint(0, 999999)}"
        raw_str = f"{secret_salt}-{datetime}-{nonce}"
        hash_val = hashlib.sha256(raw_str.encode()).hexdigest()

        uid_int = int(hash_val[:16], 16) % 1_000_000

        # 检查数据库
        if uid_int > 100_000:
            exists = db.query(User).filter(User.uid == uid_int).first()
            if not exists:
                return uid_int

    raise RuntimeError("无法生成唯一 UID（重试次数过多）")
