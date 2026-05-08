from fastapi import APIRouter,Depends,HTTPException
from models import Usuario
from dependencias import pegar_sessao,verificar_token
from main  import bcrypt_context,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES,SECRET_KEY
from schemas import UsuarioSchema,LoginSchema
from sqlalchemy.orm import Session
from jose import jwt,JWTError
from datetime import datetime,timedelta,timezone
from fastapi.security import OAuth2PasswordRequestForm

def criar_token(id_usuario,duracao_token=timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiração = datetime.now(timezone.utc) + duracao_token
    dic_info = {"sub":id_usuario,"exp":data_expiração}
    jwt_codificado= jwt.encode(dic_info,SECRET_KEY,ALGORITHM)
    return jwt_codificado

def autenticar_usuario(email,senha,session):
    usuario = session.query(Usuario).filter(Usuario.email==email).first()
    if not usuario:
        return False
    elif not bcrypt_context.verify(senha,usuario.senha):
        return False
    return usuario

    
login_router = APIRouter(prefix="/login",tags=["login"])
@login_router.post("/criar_conta" )
async def criar_conta(usuario_schema : UsuarioSchema,session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.email==usuario_schema.email).first()
    if usuario:
         raise HTTPException(
            status_code=400, detail="Email já cadastrado"
        )
    else:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome,usuario_schema.email,senha_criptografada)
        session.add(novo_usuario)
        session.commit()
        return{"mensagem":"usuário cadastrado com sucesso"}

@login_router.post("/login")
async def login(login_schema: LoginSchema,session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.email,login_schema.senha,session)
   
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id,duracao_token=timedelta(days=7))
        return{
            "access_token":access_token,
            "refresh_token":refresh_token,
            "tokeyn_type":"Bearer"

        }
@login_router.post("/login-form")
async def login_form(dado_formulario:OAuth2PasswordRequestForm = Depends(),session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(dado_formulario.username,dado_formulario.password,session)
    if not usuario:
        raise HTTPException(status_code=400, detail="Usuário não encontrado ou credenciais inválidas")
    else:
        access_token = criar_token(usuario.id)
        return{
            "access_token":access_token,

            "tokeyn_type":"Bearer"
        }
    
@login_router.get("/refresh")
async def use_refresh_token(usuario: Usuario =Depends(verificar_token)):
    #verificar o token
    access_token = criar_token(usuario.id)
    return{
            "access_token":access_token,
            "tokeyn_type":"Bearer"
        }
