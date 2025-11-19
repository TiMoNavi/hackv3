from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # --- Database ---
    DATABASE_URL: str = "sqlite:///./dev.db"

    # --- Security ---
    SECURITY_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- Mail ---
    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: Optional[str] = None
    MAIL_PORT: int = 465
    MAIL_SERVER: Optional[str] = None
    MAIL_FROM_NAME: str = ""
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True

    # --- Verification Code ---
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 5
    VERIFICATION_CODE_MIN_INTERVAL_SECONDS: int = 60

    # --- Uploads ---
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    UPLOAD_DIR: str = str(PROJECT_ROOT / "uploads")
    PUBLIC_BASE_URL: str = ""

    # --- CORS ---
    ALLOWED_ORIGINS: List[str] = ["*"]


    @field_validator("SECURITY_KEY")
    @classmethod
    def validate_security_key(cls, v: str):
        if not v or len(v) < 32:
            raise ValueError("SECURITY_KEY 未配置或长度过短(必须 >= 32)。")
        return v


    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _parse_origins(cls, v):
        # 兼容
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            if s == "":
                return []
            if s == "*":
                return ["*"]
            if s.startswith("["):
                import json
                return json.loads(s)
            return [i.strip() for i in s.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env.mysql",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
