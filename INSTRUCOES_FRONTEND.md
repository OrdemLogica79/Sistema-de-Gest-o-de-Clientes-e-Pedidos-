# 🚀 Frontend - Sistema de Gestão de Clientes

## 📋 O que foi criado

Foi desenvolvido um **frontend moderno com HTML5, CSS (Tailwind via CDN) e JavaScript Vanilla** que se integra perfeitamente ao seu backend FastAPI. O arquivo `frontend.html` contém toda a aplicação em um único arquivo.

---

## ✨ Funcionalidades Implementadas

### 1. **Página de Login** 
- ✅ Formulário para e-mail e senha
- ✅ POST para `/login/login`
- ✅ Salva o `access_token` no localStorage
- ✅ Redireciona para o Dashboard após login bem-sucedido
- ✅ Validação de erros com mensagens amigáveis

### 2. **Página de Registro**
- ✅ Modal para criar nova conta
- ✅ POST para `/login/criar_conta`
- ✅ Validação de campos
- ✅ Feedback visual de sucesso/erro

### 3. **Dashboard - Meus Clientes**
- ✅ GET para `/clientes/meus-clientes`
- ✅ Envia obrigatoriamente o cabeçalho `Authorization: Bearer <TOKEN>`
- ✅ Exibe tabela com: Nome, E-mail, Telefone, IMEI, Data Venda, Data Vencimento
- ✅ Dados descriptografados pelo backend
- ✅ Carregamento automático ao entrar na página
- ✅ Mensagem quando não há clientes cadastrados

### 4. **Dashboard - Novo Cliente**
- ✅ POST para `/clientes/cadastro`
- ✅ Formulário com todos os campos necessários
- ✅ Envia token de autorização automaticamente
- ✅ Validação de campos obrigatórios
- ✅ Feedback de sucesso/erro
- ✅ Atualiza lista de clientes após cadastro

### 5. **Segurança**
- ✅ Verificação de token ao carregar página
- ✅ Redireciona para login se não houver token
- ✅ Função de Logout limpa localStorage
- ✅ Exibe e-mail do usuário logado
- ✅ Tratamento de erros de autenticação

---

## 🛠️ Como Usar

### Passo 1: Certifique-se que o Backend está rodando

```bash
# Na pasta do projeto
uvicorn main:app --reload
```

O backend deve estar acessível em `http://127.0.0.1:8000`

### Passo 2: Abra o Frontend

Simplesmente abra o arquivo `frontend.html` em seu navegador:
- Duplo-clique no arquivo `frontend.html`, OU
- Clique com botão direito → "Abrir com navegador", OU
- Arraste o arquivo para a barra de endereços do navegador

### Passo 3: Teste as Funcionalidades

1. **Criar uma Conta:**
   - Clique em "Criar Conta"
   - Preencha: Nome, E-mail, Senha
   - Clique em "Criar Conta"

2. **Fazer Login:**
   - Use o e-mail e senha que criou
   - Clique em "Entrar"
   - Você será redirecionado para o Dashboard

3. **Listar Clientes:**
   - Na aba "Meus Clientes", você verá todos os seus clientes
   - A lista é carregada automaticamente
   - Dados sensíveis (e-mail, telefone) são descriptografados pelo backend

4. **Cadastrar Novo Cliente:**
   - Clique na aba "Novo Cliente"
   - Preencha todos os campos obrigatórios (*)
   - A data de vencimento é calculada como Data de Venda + 30 dias
   - Clique em "Cadastrar Cliente"
   - Após sucesso, a lista de clientes é atualizada automaticamente

5. **Logout:**
   - Clique no botão "Sair" no canto superior direito
   - Você será redirecionado para a página de login

---

## 📊 Detalhes Técnicos

### Endpoints Consumidos

| Método | Endpoint | Headers | Descrição |
|--------|----------|---------|-----------|
| POST | `/login/login` | - | Login de usuário |
| POST | `/login/criar_conta` | - | Criar nova conta |
| GET | `/clientes/meus-clientes` | `Authorization: Bearer {token}` | Listar meus clientes |
| POST | `/clientes/cadastro` | `Authorization: Bearer {token}` | Cadastrar novo cliente |

### Fluxo de Autenticação

1. **Login bem-sucedido:**
   ```javascript
   // Backend retorna
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "refresh_token": "...",
     "tokeyn_type": "Bearer"  // (há um typo no backend, mas funciona)
   }
   ```

2. **Token armazenado:**
   ```javascript
   localStorage.setItem('access_token', token);
   localStorage.setItem('user_email', email);
   ```

3. **Requisições autenticadas:**
   ```javascript
   headers: {
     'Authorization': `Bearer ${token}`,
     'Content-Type': 'application/json'
   }
   ```

### Storage Local (localStorage)

- `access_token`: Token JWT para requisições autenticadas
- `user_email`: E-mail do usuário logado (exibido no header)

### Tratamento de Erros

- ✅ Erros de conexão (backend não rodando)
- ✅ Credenciais inválidas
- ✅ Token expirado (redireciona para login)
- ✅ Campos obrigatórios vazios
- ✅ E-mail duplicado no cadastro

---

## 🎨 Design e UX

- **Tailwind CSS:** Tema profissional com cores azul e cinza
- **Font Awesome:** Ícones para melhor usabilidade
- **Responsivo:** Funciona em desktop, tablet e mobile
- **Feedback Visual:** Botões com hover, loading spinners, mensagens de erro/sucesso
- **Navegação Tab:** Abas para alternar entre "Meus Clientes" e "Novo Cliente"

---

## 🔧 Alterações no Backend

Foram feitas as seguintes alterações no arquivo `CadastroC.py`:

1. **Corrigido o prefixo do router:**
   - Antes: `/cadastro ` (com espaço e typo)
   - Depois: `/clientes` (sem espaço)

2. **Adicionado endpoint `/meus-clientes`:**
   - GET `/clientes/meus-clientes`
   - Requer autenticação (token Bearer)
   - Retorna clientes do usuário autenticado
   - Dados descriptografados automaticamente

3. **Adicionada autenticação ao cadastro:**
   - POST `/clientes/cadastro`
   - Agora requer o token Bearer
   - Vincula automaticamente o cliente ao `user_id` do usuário autenticado

---

## ⚠️ Considerações Importantes

1. **CORS já está configurado:**
   - O backend tem CORS ativado para aceitar requisições do frontend
   - Não é necessário fazer nenhuma configuração adicional

2. **Porta do backend:**
   - O frontend está configurado para `http://127.0.0.1:8000`
   - Se você usar outra porta, edite a variável `API_URL` no arquivo

3. **localStorage é localStorage local:**
   - O token é armazenado no localStorage do navegador
   - Será limpo ao fazer logout
   - Ao fechar o navegador, o token permanece (segurança: use HTTPS em produção)

4. **Criptografia:**
   - E-mails e telefones dos clientes são criptografados no backend com Fernet
   - O frontend recebe dados já descriptografados
   - A chave Fernet nunca é exposta ao frontend

---

## 🐛 Troubleshooting

### "Erro de conexão. Verifique se o backend está rodando"
- Verifique se o backend está em execução: `uvicorn main:app --reload`
- Verifique se está em `http://127.0.0.1:8000` (não em `localhost`)

### "Usuário não encontrado ou credenciais inválidas"
- Verifique se a conta foi criada corretamente
- Certifique-se de que está usando o e-mail e senha corretos

### Tabela de clientes não carrega
- Verifique se há clientes cadastrados para o usuário logado
- Abra o console do navegador (F12) e verifique se há erros

### Token expirado
- Faça logout e login novamente
- O token tem uma duração configurável no backend

---

## 📝 Estrutura do Arquivo

```
frontend.html (arquivo único contendo):
├── HTML (estrutura)
├── Tailwind CSS (estilos via CDN)
├── Font Awesome (ícones via CDN)
└── JavaScript Vanilla (funcionalidades)
```

---

## 🎯 Próximos Passos (Opcional)

Se quiser melhorar ainda mais:

1. Adicionar edição de clientes (PUT)
2. Adicionar exclusão de clientes (DELETE)
3. Adicionar busca/filtro de clientes
4. Adicionar paginação
5. Implementar dark mode
6. Adicionar gráficos/dashboards com dados
7. Separar em múltiplos arquivos (.html, .css, .js)
8. Fazer deploy em um servidor (Vercel, Netlify, etc.)

---

## ✅ Verificação Final

Antes de usar em produção:

- [ ] Backend está rodando em `http://127.0.0.1:8000`
- [ ] Arquivo `frontend.html` está na pasta do projeto
- [ ] Arquivo abre no navegador sem erros
- [ ] Consegue criar uma conta
- [ ] Consegue fazer login
- [ ] Consegue cadastrar um cliente
- [ ] Consegue ver os clientes listados
- [ ] Consegue fazer logout

**Tudo pronto! 🎉**
