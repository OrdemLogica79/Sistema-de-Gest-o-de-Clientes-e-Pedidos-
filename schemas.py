from pydantic import BaseModel,EmailStr,field_serializer
from datetime import date,datetime

class UsuarioSchema(BaseModel):
        nome: str
        email: EmailStr
        senha: str

class ClienteSchema(BaseModel):
        Nome_do_Cliente:str
        Email:EmailStr
        Telefone:str 
        IMEI:str 
        Data_venda: date
        Data_vencimento:date
        @field_serializer('Data_venda')
        def formatar_data(self, dt: date):
            return dt.strftime('/%d/%m/%y')

class LoginSchema(BaseModel):
       email : EmailStr
       senha : str

       class Config:
              from_attributes = True
#Aqui está a explicação detalhada de cada parte:

# 1. O Decorador @field_serializer('Data_venda')
# O que faz: Ele avisa ao Pydantic que, na hora de transformar o objeto Python em um JSON (processo chamado de serialização), ele não deve usar o padrão automático para o campo 'Data_venda', mas sim a função que vem logo abaixo
# .
# Por que usar: Por padrão, o FastAPI e o Pydantic convertem objetos de data para o formato ISO (AAAA-MM-DD)
# . Esse decorador permite que você mude isso para o formato brasileiro
# .
# 2. A Função def formatar_data(self, dt: date):
# self: Refere-se à instância do próprio schema (modelo Pydantic).
# dt: date: É o valor atual do campo Data_venda que está vindo do seu banco de dados PostgreSQL. Ele entra na função como um objeto do tipo date do Python
# .
# 3. A Lógica return dt.strftime('%d/%m/%Y')
# strftime: É um método do Python usado para formatar datas em strings (texto)
# .
# %d: Representa o dia com dois dígitos (01-31)
# .
# %m: Representa o mês com dois dígitos (01-12)
# .
# %Y: Representa o ano com quatro dígitos (ex: 2026)
# .
# Resultado: Se no banco de dados a data for 2026-05-06, o usuário da sua API receberá no JSON o texto "06/05/2026".
# Resumo do Fluxo
# Sua API busca os dados no PostgreSQL (onde a data está no formato 2026-05-06)
# .
# O SQLAlchemy entrega um objeto date para o seu Schema.
# Antes de enviar a resposta para o cliente (navegador ou robô de WhatsApp), o Pydantic executa essa função.
# O cliente recebe a data "invertida" e amigável: DD/MM/YYYY.
# Observação Importante: Esse recurso só funciona na saída de dados (Response). Se você quiser que o usuário envie datas nesse formato para a API (Request), a lógica de validação seria diferente
