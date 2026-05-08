# Sistema de Gerenciamento de Usuários e Clientes

## 📋 Descrição do Projeto

Sistema completo de API REST desenvolvido com **FastAPI** para gerenciamento de usuários e clientes com autenticação segura baseada em **JWT (JSON Web Tokens)**. A aplicação permite criar contas, realizar login, gerenciar tokens de acesso e cadastrar clientes com informações de contato, venda e datas de vigência.

O projeto utiliza **PostgreSQL** como banco de dados, **SQLAlchemy** como ORM para gerenciamento de dados, e **Alembic** para controle de versão do banco de dados.

---

## 🛠️ Tecnologias Utilizadas

- **FastAPI**: Framework web moderno e de alta performance para construção de APIs REST
- **SQLAlchemy 2.0**: ORM para abstração e gerenciamento do banco de dados
- **PostgreSQL**: Banco de dados relacional
- **Alembic**: Ferramenta de migração de banco de dados
- **Pydantic**: Validação de dados e serialização
- **Python-Jose**: Implementação de JWT para autenticação
- **Passlib + Bcrypt**: Criptografia segura de senhas
- **python-dotenv**: Gerenciamento de variáveis de ambiente

---

## 📁 Estrutura do Projeto

```
.
├── main.py                  # Arquivo principal da aplicação FastAPI
├── models.py               # Modelos do banco de dados (ORM)
├── schemas.py              # Schemas Pydantic para validação de dados
├── database.py             # Configuração de conexão com PostgreSQL
├── login.py                # Rotas e funções de autenticação
├── CadastroC.py            # Rotas de cadastro de clientes
├── dependencias.py         # Dependências compartilhadas (middlewares, funções auxiliares)
├── alembic/                # Pasta de migrações do banco de dados
│   ├── env.py             # Configuração do Alembic
│   ├── script.py.mako     # Template para novas migrações
│   └── versions/          # Histórico de migrações aplicadas
├── requirements.txt        # Dependências do projeto
├── alembic.ini            # Arquivo de configuração do Alembic
└── .env                   # Variáveis de ambiente (não incluído no repositório)
```

---

## ✨ Funcionalidades Principais

### Autenticação e Usuários
- **Criar Conta**: Registro de novos usuários com validação de email único
- **Login**: Autenticação com email e senha
- **Criptografia de Senhas**: Senhas armazenadas com bcrypt
- **JWT Tokens**: Geração de access_token e refresh_token
- **Refresh Token**: Renovação de tokens sem fazer login novamente

### Gerenciamento de Clientes
- **Cadastro de Clientes**: Registro de novos clientes com informações de contato
- **Dados Capturados**:
  - Nome do cliente
  - Email (único)
  - Telefone
  - IMEI (identificador do dispositivo)
  - Data de venda
  - Data de vencimento (calculada automaticamente: 30 dias após data de venda)

### Formatação de Datas
- Conversão automática de datas para formato brasileiro (DD/MM/YYYY)
- Validação de emails com EmailStr do Pydantic

---

## 📋 Requisitos

- Python 3.8+
- PostgreSQL 12+
- pip (gerenciador de pacotes do Python)
- Virtual Environment (venv)

---

## 🚀 Instalação

### 1. Clone ou extraia o repositório
```bash
cd seu-projeto
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
```

### 3. Ative o ambiente virtual

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instale as dependências
```bash
pip install -r requirements.txt
```

### 5. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Configuração do Banco de Dados
CONEXAO=postgresql://usuario:senha@localhost:5432/nome_banco

# Configuração JWT
SECRET_KEY=sua_chave_secreta_muito_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 6. Execute as migrações do banco de dados

```bash
alembic upgrade head
```

### 7. Inicie a aplicação

```bash
uvicorn main:app --reload
```

A API estará disponível em: `http://localhost:8000`

Documentação automática: `http://localhost:8000/docs` (Swagger UI)

---

## 📡 Endpoints da API

### Autenticação

#### 1. Criar Conta
```
POST /login/criar_conta
```
**Body:**
```json
{
  "nome": "João Silva",
  "email": "joao@example.com",
  "senha": "senha123"
}
```
**Resposta (200):**
```json
{
  "mensagem": "usuário cadastrado com sucesso"
}
```

#### 2. Login
```
POST /login/login
```
**Body:**
```json
{
  "email": "joao@example.com",
  "senha": "senha123"
}
```
**Resposta (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

#### 3. Refresh Token
```
GET /login/refresh
```
**Header:**
```
Authorization: Bearer <access_token>
```
**Resposta (200):**
```json
{
  "access_token": "novo_token_aqui",
  "token_type": "Bearer"
}
```

### Clientes

#### 1. Cadastrar Cliente
```
POST /cadastro/criar_cadastro
```
**Body:**
```json
{
  "Nome_do_Cliente": "Empresa XYZ",
  "Email": "contato@empresa.com",
  "Telefone": "(11) 98765-4321",
  "IMEI": "123456789012345",
  "Data_venda": "2026-05-08",
  "Data_vencimento": "2026-06-07"
}
```
**Resposta (200):**
```json
{
  "mensagem": "Tudo Certo!"
}
```

---

## 🔐 Autenticação

A API utiliza **OAuth2 com JWT (Bearer tokens)** para autenticação.

### Como usar:
1. Faça login e receba um `access_token`
2. Inclua o token em todas as requisições protegidas:
   ```
   Authorization: Bearer <seu_token_aqui>
   ```
3. Quando o token expirar (padrão: 30 minutos), use o `refresh_token` para obter um novo

---

## 📊 Modelos de Dados

### Usuário
```python
{
  "id": int (autoincremento),
  "nome": str,
  "email": str (único),
  "senha": str (criptografada)
}
```

### Cliente
```python
{
  "id": int (autoincremento),
  "Nome_do_Cliente": str,
  "Email": str (único),
  "Telefone": str,
  "IMEI": str,
  "Data_venda": date,
  "Data_vencimento": date (calculada automaticamente: data_venda + 30 dias)
}
```

---

## 🔄 Migrações de Banco de Dados

O projeto utiliza **Alembic** para versionamento do banco de dados.

### Criar uma nova migração automática
```bash
alembic revision --autogenerate -m "Descrição da mudança"
```

### Aplicar todas as migrações pendentes
```bash
alembic upgrade head
```

### Voltar uma versão
```bash
alembic downgrade -1
```

### Ver histórico de migrações
```bash
alembic history
```

---

## 🛡️ Segurança

- **Senhas**: Criptografadas com bcrypt (algoritmo seguro)
- **Tokens JWT**: Assinados com chave secreta, expiram em 30 minutos
- **Email Único**: Validação de email duplicado no cadastro de usuários e clientes
- **CORS**: Middleware configurado para controle de origem
- **Validação de Dados**: Todos os inputs validados com Pydantic

---

## 🐛 Tratamento de Erros

A API retorna códigos HTTP apropriados:

| Código | Significado |
|--------|-------------|
| 200 | Sucesso |
| 400 | Requisição inválida (ex: email duplicado) |
| 401 | Não autenticado |
| 403 | Não autorizado |
| 500 | Erro interno do servidor |

---

## 💡 Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `CONEXAO` | String de conexão PostgreSQL | `postgresql://user:pass@localhost:5432/db` |
| `SECRET_KEY` | Chave para assinar JWT | `sua_chave_secreta_muito_segura` |
| `ALGORITHM` | Algoritmo de assinatura JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo de expiração do token | `30` |

---

## 📝 Observações Importantes

1. **Formatação de Datas**: As datas são automaticamente convertidas para o formato brasileiro (DD/MM/YYYY) nas respostas JSON
2. **Email Único**: Os emails devem ser únicos tanto para usuários quanto para clientes
3. **Data de Vencimento**: É calculada automaticamente como 30 dias após a data de venda
4. **Tokens**: O `access_token` expira em 30 minutos (configurável), enquanto o `refresh_token` dura 7 dias

---

## 📞 Suporte

Para dúvidas ou problemas, verifique:
- Logs da aplicação
- Documentação automática em `/docs`
- Status do banco de dados PostgreSQL
- Variáveis de ambiente configuradas corretamente

---

## 📄 Licença

[Adicione sua licença aqui]

---

**Desenvolvido com ❤️ usando FastAPI e Python**
