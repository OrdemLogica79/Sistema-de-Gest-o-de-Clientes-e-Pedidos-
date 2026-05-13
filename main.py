from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import redis
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware


def _parse_list_env(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default

    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        pass

    return [item.strip() for item in value.split(",") if item.strip()]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()
SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
ALGORITHM = os.getenv("ALGORITHM", "HS256").strip()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "3"))
CHAVE_F = os.getenv("CHAVE_F", "").strip()
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
REDIS_URL = os.getenv("REDIS_URL", "").strip()
origins = _parse_list_env(
    os.getenv("ORIGINS"),
    ["http://127.0.0.1:5000"] if ENVIRONMENT == "development" else [],
)
allowed_hosts = _parse_list_env(
    os.getenv("ALLOWED_HOSTS"),
    ["127.0.0.1", "localhost"]
    if ENVIRONMENT == "development"
    else ["seu-dominio.com"],
)

if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("SECRET_KEY inválido ou muito curto (mínimo: 32 caracteres)")
if not CHAVE_F:
    raise ValueError("CHAVE_F não configurada")

try:
    fernet = Fernet(CHAVE_F.encode())
except Exception as exc:
    raise ValueError("CHAVE_F inválida para Fernet") from exc

if not DATABASE_URL:
    logger.warning("DATABASE_URL não foi definido no ambiente")

limiter_storage_uri = "memory://"
if REDIS_URL:
    try:
        redis.from_url(REDIS_URL).ping()
        limiter_storage_uri = REDIS_URL
    except Exception as exc:
        logger.warning(
            "Redis indisponível para rate limiting, usando memória local: %s",
            str(exc),
        )

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=limiter_storage_uri,
    headers_enabled=True,
)

app = FastAPI(
    title="Sistema de Gestão de Clientes",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Total-Count"],
    max_age=3600,
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

if ENVIRONMENT == "production":

    @app.middleware("http")
    async def force_https(request: Request, call_next):
        if request.url.scheme == "http":
            secure_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(secure_url), status_code=301)
        return await call_next(request)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = datetime.now(timezone.utc)
    response = await call_next(request)
    duration = (datetime.now(timezone.utc) - start_time).total_seconds()

    logger.info(
        "Method=%s | Path=%s | Status=%s | Duration=%.2fs | IP=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration,
        request.client.host if request.client else "unknown",
    )
    return response


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer(tokenUrl="/login/login", auto_error=False)

from login import login_router
from CadastroC import cliente_router
from robo_lembrete_vencimento import (
    start_due_reminder_worker,
    stop_due_reminder_worker,
)

app.include_router(login_router)
app.include_router(cliente_router)


@app.on_event("startup")
def startup_events() -> None:
    start_due_reminder_worker()


@app.on_event("shutdown")
def shutdown_events() -> None:
    stop_due_reminder_worker()


@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/", include_in_schema=False)
async def serve_index():
    index_file = BASE_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html não encontrado")
    return FileResponse(index_file)


logger.info("Aplicação iniciada em modo: %s", ENVIRONMENT)
