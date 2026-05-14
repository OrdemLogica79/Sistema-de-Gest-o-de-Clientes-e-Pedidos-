from fastapi import FastAPI
from dotenv import load_dotenv
from passlib.context import CryptContext 
from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from datetime import datetime, timedelta,timezone
import os
from fastapi.middleware.cors import CORSMiddleware
from cryptography.fernet import Fernet


load_dotenv()
ORIGINS = os.getenv("ORIGINS", "*")  # Default para "*" se não estiver no .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM  = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
CHAVE_F = os.getenv("CHAVE_F")
DATABASE_URL = os.getenv("DATABASE_URL")
app = FastAPI()

# Configuração CORS permissiva para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todos os domínios para testes
    allow_credentials=False,  # Desabilitado quando usar "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

fernet = Fernet(CHAVE_F)
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer (tokenUrl="login/login-form")

from login import login_router
from CadastroC import cliente_router


app.include_router(login_router)
app.include_router(cliente_router)
