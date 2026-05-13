from datetime import datetime, timedelta, timezone
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from dependencias import pegar_sessao, revogar_token, verificar_refresh_token, verificar_token
from main import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    ENVIRONMENT,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    bcrypt_context,
    limiter,
)
from models import Usuario
from schemas import LoginSchema, UsuarioSchema
from seguranca import criptografar_dado, descriptografar_dado

logger = logging.getLogger(__name__)

login_router = APIRouter(prefix="/login", tags=["login"])


def criar_token(id_usuario: int, duracao_token: timedelta, tipo: str) -> str:
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {
        "sub": str(id_usuario),
        "exp": data_expiracao,
        "jti": str(uuid.uuid4()),
        "type": tipo,
    }
    return jwt.encode(dic_info, SECRET_KEY, algorithm=ALGORITHM)


def autenticar_usuario(email: str, senha: str, session: Session) -> Usuario | None:
    usuario = None
    dummy_hash = bcrypt_context.hash("dummy-password-for-timing-protection")

    usuarios = session.query(Usuario).all()
    for item in usuarios:
        try:
            email_desc = descriptografar_dado(item.email)
            if email_desc == email:
                usuario = item
                break
        except Exception as exc:
            logger.warning("Erro ao descriptografar e-mail de usuário: %s", str(exc))
            continue

    if usuario and bcrypt_context.verify(senha, usuario.senha):
        return usuario

    # Mantém tempo de resposta consistente mesmo quando o usuário não existe.
    bcrypt_context.verify(senha, dummy_hash)
    return None


def _cookie_secure() -> bool:
    return ENVIRONMENT == "production"


@login_router.post("/criar_conta")
@limiter.limit("3/hour")
async def criar_conta(
    request: Request,
    response: Response,
    usuario_schema: UsuarioSchema,
    session: Session = Depends(pegar_sessao),
):
    _ = response

    usuarios = session.query(Usuario).all()
    for item in usuarios:
        try:
            email_desc = descriptografar_dado(item.email)
            if email_desc == usuario_schema.email:
                logger.warning("Tentativa de cadastro com e-mail duplicado: %s", usuario_schema.email)
                raise HTTPException(status_code=400, detail="Erro ao processar solicitação")
        except HTTPException:
            raise
        except Exception:
            continue

    try:
        email_criptografado = criptografar_dado(usuario_schema.email)
        senha_hash = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome, email_criptografado, senha_hash)
        session.add(novo_usuario)
        session.commit()
        logger.info("Novo usuário registrado: ID %s", novo_usuario.id)
        return {"mensagem": "Usuário cadastrado com sucesso"}
    except Exception as exc:
        logger.error("Erro ao registrar usuário: %s", str(exc))
        raise HTTPException(status_code=500, detail="Erro ao processar solicitação")


@login_router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    login_schema: LoginSchema,
    session: Session = Depends(pegar_sessao),
):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        logger.warning(
            "Falha de login para %s | IP=%s",
            login_schema.email,
            request.client.host if request.client else "unknown",
        )
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token = criar_token(
        usuario.id,
        duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        tipo="access",
    )
    refresh_token = criar_token(
        usuario.id,
        duracao_token=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        tipo="refresh",
    )

    logger.info("Login bem-sucedido: Usuario ID %s", usuario.id)

    response = JSONResponse(
        content={"mensagem": "Login realizado com sucesso", "token_type": "Bearer"}
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=_cookie_secure(),
        samesite="Strict",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=_cookie_secure(),
        samesite="Strict",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )
    return response


@login_router.post("/logout")
async def logout(
    request: Request,
    usuario: Usuario = Depends(verificar_token),
):
    token = request.cookies.get("access_token")

    try:
        if token:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            jti = decoded.get("jti")
            exp = decoded.get("exp")
            if jti and exp:
                revogar_token(jti, exp)

        logger.info("Logout: Usuario ID %s", usuario.id)
        response = JSONResponse(content={"mensagem": "Logout realizado com sucesso"})
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")
        return response
    except JWTError as exc:
        logger.error("Erro JWT no logout: %s", str(exc))
        raise HTTPException(status_code=401, detail="Erro ao fazer logout")
    except Exception as exc:
        logger.error("Erro ao fazer logout: %s", str(exc))
        raise HTTPException(status_code=500, detail="Erro ao fazer logout")


@login_router.post("/refresh")
async def refresh_token(
    request: Request,
    usuario: Usuario = Depends(verificar_refresh_token),
):
    _ = request  # request necessário para manter interface consistente
    access_token = criar_token(
        usuario.id,
        duracao_token=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        tipo="access",
    )

    response = JSONResponse(content={"token_type": "Bearer"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=_cookie_secure(),
        samesite="Strict",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return response
