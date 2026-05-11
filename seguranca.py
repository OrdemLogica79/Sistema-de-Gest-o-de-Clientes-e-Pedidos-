import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()


CHAVE_F = os.getenv("CHAVE_F")
fernet = Fernet(CHAVE_F)

def criptografar_dado(texto: str) -> str:
    return fernet.encrypt(texto.encode()).decode()

def descriptografar_dado(texto_criptografado: str) -> str:
    return fernet.decrypt(texto_criptografado.encode()).decode()