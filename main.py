from fastapi import FastAPI
from dotenv import load_dotenv
from passlib.context import CryptContext 
from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from datetime import datetime, timedelta,timezone
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM  = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

app = FastAPI()

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_schema = OAuth2PasswordBearer (tokenUrl="login/login-form")

from login import login_router
from CadastroC import cliente_router


app.include_router(login_router)
app.include_router(cliente_router)
