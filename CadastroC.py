from fastapi import APIRouter,Depends,HTTPException
from models import Cliente
from database import engine
from dependencias import pegar_sessao
from passlib.context import CryptContext
from main import bcrypt_context
from schemas import ClienteSchema
from sqlalchemy.orm import Session
from seguranca import criptografar_dado

cliente_router = APIRouter(prefix="/cadastro ",tags=["cadastro"])

@cliente_router.post("/cadastro" )
async def cadastro_cliente(cliente_schema : ClienteSchema,session = Depends (pegar_sessao)):
    if True:
        email_protegido = criptografar_dado (cliente_schema.Email)
        telefone_protegido= criptografar_dado(cliente_schema.Telefone)
        novo_cliente = Cliente(cliente_schema.Nome_do_Cliente,email_protegido,telefone_protegido,cliente_schema.IMEI,cliente_schema.Data_venda,cliente_schema.Data_vencimento)
        session.add(novo_cliente)
        session.commit()
        return{"mensagem":"Tudo Certo!"}
