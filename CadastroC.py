import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import conint
from sqlalchemy.orm import Session

from dependencias import pegar_sessao, verificar_token
from main import limiter
from models import Cliente, Usuario
from schemas import ClienteSchema
from seguranca import criptografar_dado, descriptografar_dado

logger = logging.getLogger(__name__)

cliente_router = APIRouter(prefix="/clientes", tags=["clientes"])


@cliente_router.post("/cadastro")
@limiter.limit("10/minute")
async def cadastro_cliente(
    request: Request,
    response: Response,
    cliente_schema: ClienteSchema,
    session: Session = Depends(pegar_sessao),
    usuario_atual: Usuario = Depends(verificar_token),
):
    _ = request
    _ = response

    try:
        email_protegido = criptografar_dado(cliente_schema.Email)
        telefone_protegido = criptografar_dado(cliente_schema.Telefone)
        imei_protegido = criptografar_dado(cliente_schema.IMEI)

        novo_cliente = Cliente(
            usuario_atual.id,
            cliente_schema.Nome_do_Cliente,
            email_protegido,
            telefone_protegido,
            imei_protegido,
            cliente_schema.Data_venda,
            None,
        )
        session.add(novo_cliente)
        session.commit()

        logger.info(
            "Cliente cadastrado: ID %s | Usuario ID %s",
            novo_cliente.id,
            usuario_atual.id,
        )
        return {"mensagem": "Cliente cadastrado com sucesso!", "id": novo_cliente.id}
    except Exception as exc:
        logger.error("Erro ao cadastrar cliente: %s", str(exc))
        raise HTTPException(status_code=500, detail="Erro ao cadastrar cliente")


@cliente_router.get("/meus-clientes")
async def listar_clientes(
    session: Session = Depends(pegar_sessao),
    usuario_atual: Usuario = Depends(verificar_token),
):
    try:
        clientes_db = (
            session.query(Cliente).filter(Cliente.user_id == usuario_atual.id).all()
        )
        if not clientes_db:
            return []

        resposta = []
        for cliente in clientes_db:
            resposta.append(
                {
                    "id": cliente.id,
                    "nome": cliente.Nome_do_Cliente,
                    "telefone": descriptografar_dado(cliente.Telefone),
                    "email": descriptografar_dado(cliente.Email),
                    "imei": descriptografar_dado(cliente.IMEI),
                    "data_venda": str(cliente.Data_venda),
                    "data_vencimento": str(cliente.Data_vencimento),
                }
            )

        logger.info(
            "Listagem de clientes: Usuario ID %s | Total=%s",
            usuario_atual.id,
            len(resposta),
        )
        return resposta
    except Exception as exc:
        logger.error("Erro ao listar clientes: %s", str(exc))
        raise HTTPException(status_code=500, detail="Erro ao listar clientes")


@cliente_router.delete("/deletar/{cliente_id}")
async def deletar_cliente(
    cliente_id: conint(gt=0),
    session: Session = Depends(pegar_sessao),
    usuario_atual: Usuario = Depends(verificar_token),
):
    try:
        cliente = (
            session.query(Cliente)
            .filter(Cliente.id == cliente_id, Cliente.user_id == usuario_atual.id)
            .first()
        )

        if not cliente:
            logger.warning(
                "Tentativa não autorizada de delete: Cliente ID %s | Usuario ID %s",
                cliente_id,
                usuario_atual.id,
            )
            raise HTTPException(
                status_code=404, detail="Cliente não encontrado ou sem permissão"
            )

        session.delete(cliente)
        session.commit()
        logger.info(
            "Cliente deletado: Cliente ID %s | Usuario ID %s",
            cliente_id,
            usuario_atual.id,
        )
        return {"mensagem": "Cliente deletado com sucesso!"}
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Erro ao deletar cliente: %s", str(exc))
        raise HTTPException(status_code=500, detail="Erro ao deletar cliente")
