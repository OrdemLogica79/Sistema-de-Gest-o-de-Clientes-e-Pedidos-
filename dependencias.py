from fastapi import Depends, HTTPException
from sqlalchemy.orm import sessionmaker,Session
from models import Usuario
from database import engine
from jose import jwt,JWTError
from main import SECRET_KEY,ALGORITHM,oauth2_schema



def pegar_sessao():
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
    finally:
        session.close()


def verificar_token(token: str =Depends(oauth2_schema),session: Session = Depends(pegar_sessao)):
    try:
        dic_info = jwt.decode(token,SECRET_KEY,ALGORITHM)
        id_usuario = int(dic_info.get("sub"))
    except JWTError as erro :
        print(erro)
        raise HTTPException(status_code=401,detail="Acesso Negado,verifique a validade do token")
        #verificar se o token é válido 
        #extrair do token o ID do usuario do token
    usuario = session.query(Usuario).filter(Usuario.id==id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401,detail="Acesso Inválido")
    return usuario
