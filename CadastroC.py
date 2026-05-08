from fastapi import APIRouter,Depends,HTTPException
from models import Cliente
from database import engine
from dependencias import pegar_sessao
from passlib.context import CryptContext
from main import bcrypt_context
from schemas import ClienteSchema
from sqlalchemy.orm import Session

cliente_router = APIRouter(prefix="/cadastro ",tags=["cadastro"])

@cliente_router.post("/criar_cadastro" )
async def cadastro_cliente(cliente_schema : ClienteSchema,session :Session = Depends (pegar_sessao)):
    if True:
        novo_cliente = Cliente(cliente_schema.Nome_do_Cliente,cliente_schema.Email,cliente_schema.Telefone ,cliente_schema.IMEI,cliente_schema.Data_venda,cliente_schema.Data_vencimento)
        session.add(novo_cliente)
        session.commit()
        return{"mensagem":"Tudo Certo!"}
