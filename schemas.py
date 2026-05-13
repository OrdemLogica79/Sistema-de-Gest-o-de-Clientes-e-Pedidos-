from datetime import date
import re
from typing import Optional

from pydantic import BaseModel, EmailStr, constr, field_validator


class UsuarioSchema(BaseModel):
    nome: constr(min_length=2, max_length=100)
    email: EmailStr
    senha: str

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, valor: str) -> str:
        if len(valor) < 12:
            raise ValueError("Senha deve ter no mínimo 12 caracteres")
        if not re.search(r"[A-Z]", valor):
            raise ValueError("Senha deve conter letra maiúscula")
        if not re.search(r"[a-z]", valor):
            raise ValueError("Senha deve conter letra minúscula")
        if not re.search(r"\d", valor):
            raise ValueError("Senha deve conter número")
        if not re.search(r"[!@#$%^&*]", valor):
            raise ValueError("Senha deve conter caractere especial (!@#$%^&*)")
        return valor


class ClienteSchema(BaseModel):
    Nome_do_Cliente: constr(min_length=2, max_length=150)
    Email: EmailStr
    Telefone: constr(min_length=8, max_length=20)
    IMEI: constr(pattern=r"^\d{15}$")
    Data_venda: date
    Data_vencimento: Optional[date] = None


class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

    class Config:
        from_attributes = True
