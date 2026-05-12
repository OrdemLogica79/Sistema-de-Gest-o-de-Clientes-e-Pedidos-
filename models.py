from sqlalchemy import Column,String,Integer,Boolean, Float,ForeignKey,Date
from datetime import timedelta
from database import Base
from passlib.context import CryptContext




class Usuario(Base):
    __tablename__ ="usuarios"

    id = Column("id",Integer,primary_key=True,autoincrement=True)
    nome = Column ("nome",String)
    email = Column ("email",String,nullable=False)
    senha = Column ("senha",String,nullable=False)

    def __init__(self,nome,email,senha):
        self.nome = nome
        self.email = email
        self.senha = senha

class Cliente(Base):
    __tablename__ ="clientes"

    user_id = Column ("user_id",Integer,ForeignKey("usuarios.id"),nullable=False)
    id = Column("Id",Integer,primary_key=True,autoincrement=True)
    Nome_do_Cliente = Column("Nome_do_Cliente",String)
    Email = Column("Email",String,unique=True)
    Telefone = Column("Telefone",String)
    IMEI = Column("IMEI",String)
    Data_venda = Column("Data_venda",Date)
    Data_vencimento = Column("Data_vencimento",Date)

    def __init__(self,user_id,Nome_do_Cliente,Email,Telefone,IMEI, Data_venda, Data_vencimento,):
        
        self.user_id = user_id
        self.Nome_do_Cliente = Nome_do_Cliente
        self.Email = Email
        self.Telefone = Telefone
        self.IMEI = IMEI
        self.Data_venda = Data_venda
        if self.Data_venda:
            # Soma os 30 dias ao valor da data informada [3]
            self.Data_vencimento = self.Data_venda + timedelta(days=30)
