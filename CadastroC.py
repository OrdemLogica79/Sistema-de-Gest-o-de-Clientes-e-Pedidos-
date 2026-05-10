from fastapi import APIRouter,Depends,HTTPException
from models import Cliente
from database import engine
from dependencias import pegar_sessao
from passlib.context import CryptContext
from main import bcrypt_context
from schemas import ClienteSchema
from sqlalchemy.orm import Session

cliente_router = APIRouter(prefix="/cadastro ",tags=["cadastro"])

@cliente_router.post("/cadastro" )
async def cadastro_cliente(cliente_schema : ClienteSchema,session :Session = Depends (pegar_sessao)):
    if True:
        novo_cliente = Cliente(cliente_schema.Nome_do_Cliente,cliente_schema.Email,cliente_schema.Telefone ,cliente_schema.IMEI,cliente_schema.Data_venda,cliente_schema.Data_vencimento)
        return{"mensagem":"Tudo Certo!"}

@cliente_router.delete("/apagar")
async def delete_cliente(cliente_schema : ClienteSchema,session :Session = Depends (pegar_sessao)):
    cliente = session.query(Cliente).filter(Cliente.id ==cliente_schema.id ).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Soft Delete: apenas marcamos como inativo
    cliente.ativo = False 
    session.commit()
