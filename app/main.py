from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

import os
from dotenv import load_dotenv
# 显式加载 MySQL 环境文件
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env.mysql"))

from app.db.session import engine, Base
from app.models import * # noqa: F401,F403
from sqlalchemy.engine import url as sa_url
from fastapi.exceptions import RequestValidationError
from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.response import err
from app.routers.auth_router import router as auth_router
from app.routers.user_router import router as user_router
from app.routers.registration_router import router as registration_router
from app.routers.project_router import router as project_router
from app.routers.upload_router import router as upload_router


app = FastAPI(title="Event Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIR), name="static")


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(registration_router)
app.include_router(project_router)
app.include_router(upload_router)


if not settings.SECURITY_KEY or len(settings.SECURITY_KEY) < 32:
    raise RuntimeError("SECURITY_KEY 未配置或长度过短(>=32)。请在 .env.mysql 中设置 SECURITY_KEY。")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = exc.errors()
    return err("参数校验失败", code=42200, data=details, status_code=422)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return err(str(exc.detail), code=exc.status_code * 100, status_code=exc.status_code)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # 这是你正确的全局 500 处理器
    return err("服务器内部错误", code=50000, status_code=500)


@app.on_event("startup")
def on_startup():
    try:
        u = sa_url.make_url(settings.DATABASE_URL)
        print("[DB] dialect:", u.get_backend_name(), "driver:", u.get_driver_name())
        print("[DB] host:", u.host, "port:", u.port, "database:", u.database)
    except Exception as e:
        print("[DB] parse error:", e)
    Base.metadata.create_all(bind=engine)
    print("[OK] Database tables ensured. Models:", list(Base.metadata.tables.keys()))


@app.get("/healthz")
def healthz():
    from datetime import datetime, timezone
    return {"ok": True, "time": datetime.now(timezone.utc).isoformat()}

