from fastapi import APIRouter,Depends,HTTPException
from models import Cliente, Usuario
from database import engine
from dependencias import pegar_sessao, verificar_token
from passlib.context import CryptContext
from main import bcrypt_context, fernet
from schemas import ClienteSchema
from sqlalchemy.orm import Session
from seguranca import criptografar_dado, descriptografar_dado

cliente_router = APIRouter(prefix="/clientes", tags=["clientes"])

@cliente_router.post("/cadastro")
async def cadastro_cliente(cliente_schema: ClienteSchema, usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    """Cadastra um novo cliente vinculado ao usuário autenticado"""
    try:
        email_protegido = criptografar_dado(cliente_schema.Email)
        telefone_protegido = criptografar_dado(cliente_schema.Telefone)
        novo_cliente = Cliente(
            user_id=usuario.id,
            Nome_do_Cliente=cliente_schema.Nome_do_Cliente,
            Email=email_protegido,
            Telefone=telefone_protegido,
            IMEI=cliente_schema.IMEI,
            Data_venda=cliente_schema.Data_venda,
            Data_vencimento=cliente_schema.Data_vencimento
        )
        session.add(novo_cliente)
        session.commit()
        return {"mensagem": "Cliente cadastrado com sucesso!"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Erro ao cadastrar cliente: {str(e)}")

@cliente_router.get("/meus-clientes")
async def listar_meus_clientes(usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    """Lista todos os clientes do usuário autenticado com dados descriptografados"""
    try:
        clientes = session.query(Cliente).filter(Cliente.user_id == usuario.id).all()
        
        clientes_descriptografados = []
        for cliente in clientes:
            cliente_dict = {
                "id": cliente.id,
                "Nome_do_Cliente": cliente.Nome_do_Cliente,
                "Email": descriptografar_dado(cliente.Email),
                "Telefone": descriptografar_dado(cliente.Telefone),
                "IMEI": cliente.IMEI,
                "Data_venda": cliente.Data_venda.strftime('%d/%m/%Y') if cliente.Data_venda else None,
                "Data_vencimento": cliente.Data_vencimento.strftime('%d/%m/%Y') if cliente.Data_vencimento else None
            }
            clientes_descriptografados.append(cliente_dict)
        
        return clientes_descriptografados
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao listar clientes: {str(e)}")
