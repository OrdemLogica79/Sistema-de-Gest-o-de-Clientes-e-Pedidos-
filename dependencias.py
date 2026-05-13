from datetime import datetime, timezone
import logging
import os

from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
import redis
from sqlalchemy.orm import Session, sessionmaker

from database import engine
from main import ALGORITHM, SECRET_KEY, oauth2_schema
from models import Usuario

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "").strip()
_fallback_blacklist: set[str] = set()
_redis_client = None

if REDIS_URL:
    try:
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        _redis_client.ping()
        logger.info("Token blacklist configurada com Redis")
    except Exception as exc:
        _redis_client = None
        logger.warning("Falha ao conectar no Redis, usando fallback em memória: %s", str(exc))


def _blacklist_key(jti: str) -> str:
    return f"token_blacklist:{jti}"


def revogar_token(jti: str, exp_claim: int) -> None:
    now_ts = int(datetime.now(timezone.utc).timestamp())
    ttl = max(1, int(exp_claim) - now_ts)

    if _redis_client:
        _redis_client.setex(_blacklist_key(jti), ttl, "1")
        return

    _fallback_blacklist.add(jti)


def token_revogado(jti: str) -> bool:
    if _redis_client:
        return _redis_client.exists(_blacklist_key(jti)) == 1
    return jti in _fallback_blacklist


def pegar_sessao():
    try:
        session_local = sessionmaker(bind=engine)
        session = session_local()
        yield session
    finally:
        session.close()


def _extrair_token(request: Request, token_header: str | None) -> str:
    if token_header:
        return token_header

    token_cookie = request.cookies.get("access_token")
    if token_cookie:
        return token_cookie

    raise HTTPException(status_code=401, detail="Token ausente")


def _validar_e_buscar_usuario(
    token: str,
    session: Session,
    tipo_esperado: str = "access",
) -> Usuario:
    try:
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        jti = dic_info.get("jti")
        if not jti or token_revogado(jti):
            raise HTTPException(status_code=401, detail="Token revogado ou inválido")

        token_type = dic_info.get("type")
        if token_type != tipo_esperado:
            raise HTTPException(status_code=401, detail="Tipo de token inválido")

        id_usuario = int(dic_info.get("sub"))
    except HTTPException:
        raise
    except JWTError as erro:
        logger.error("Erro ao decodificar token: %s", str(erro))
        raise HTTPException(status_code=401, detail="Acesso negado")
    except Exception as exc:
        logger.error("Erro inesperado ao validar token: %s", str(exc))
        raise HTTPException(status_code=401, detail="Acesso negado")

    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        logger.warning("Usuário não encontrado: ID %s", id_usuario)
        raise HTTPException(status_code=401, detail="Acesso inválido")

    return usuario


def verificar_token(
    request: Request,
    token_header: str | None = Depends(oauth2_schema),
    session: Session = Depends(pegar_sessao),
):
    token = _extrair_token(request, token_header)
    return _validar_e_buscar_usuario(token, session, tipo_esperado="access")


def verificar_refresh_token(
    request: Request,
    session: Session = Depends(pegar_sessao),
):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token ausente")

    return _validar_e_buscar_usuario(token, session, tipo_esperado="refresh")
