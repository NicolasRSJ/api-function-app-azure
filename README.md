# API de Usuários com Azure Functions (Python)

Este projeto contém uma **API HTTP em Azure Functions (Python)** para cadastro e gerenciamento de usuários.  
Ela expõe endpoints para **listar, criar, atualizar e remover** usuários via HTTP, armazenando os dados em um **banco Azure SQL Database**.

---

## Pré-requisitos

Antes de usar este repositório, você precisa ter:

- Uma conta no **Microsoft Azure**
- Uma **Function App** criada no Azure (runtime **Python**)
- Um **Azure SQL Database** criado (servidor + banco de dados)
- **Git** instalado
- **Azure Functions Core Tools** instalado (`func`)
- **Azure CLI** instalado (`az`)
- (Opcional) **Azure Data Studio** ou **extensão SQL Server no VS Code** para gerenciar o banco

---

## Criando a Function App no Azure

1. Acesse o **Portal Azure**.
2. Clique em **Create a resource** → **Function App**.
3. Preencha os campos principais:
   - **Subscription**: escolha sua assinatura
   - **Resource Group**: crie ou use um existente (ex: `rg-functions-aula`)
   - **Function App name**: um nome único (ex: `apiusuarios-nicolas`)
   - **Publish**: `Code`
   - **Runtime stack**: `Python`
   - **Version**: 3.10 ou outra versão suportada
   - **Region**: região de sua preferência
4. Avance com **Next** até o final e clique em **Create**.
5. Aguarde o deploy terminar.

> Guarde o **nome da Function App**, vamos usar ele no comando de publicação:
> `NOME_DA_FUNCTIONAPP` (ex: `apiusuarios-nicolas`).

---

## Configurando o banco de dados SQL no Azure

### Criar servidor e banco (se ainda não existir)

1. No portal, crie um recurso **SQL Database**.
2. Durante a criação:
   - Crie um **servidor SQL** (ex: `srv-aularafael-sql.database.windows.net`).
   - Defina um **login e senha de administrador** do servidor (ex: usuário `sqladmin`).
   - Defina o nome do banco (ex: `dbaularafael`).

> Certifique-se de habilitar a opção para permitir acesso de **Azure services** ao servidor SQL.

### Criar a tabela `Usuarios`

Conecte no banco (via Azure Data Studio, Query Editor do portal ou VS Code) e execute:

```sql
CREATE TABLE Usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nome   NVARCHAR(100) NOT NULL,
    idade  INT           NOT NULL,
    email  NVARCHAR(255) NOT NULL,
    cidade NVARCHAR(100) NULL
);
```
### Configurar a connection string na Function App

1. No portal, abra a sua **Function App**.
2. Vá em **Configuration** → aba **Application settings**.
3. Clique em **New application setting** e crie a chave:

   - **Name**: `SQL_CONNECTION_STRING`
   - **Value** (exemplo):

     ```text
     Driver={ODBC Driver 18 for SQL Server};
     Server=tcp:SEU-SERVIDOR.database.windows.net,1433;
     Database=SEU_BANCO;
     Uid=SEU_USUARIO_SQL;
     Pwd=SUA_SENHA_SQL;
     Encrypt=yes;
     TrustServerCertificate=no;
     Connection Timeout=30;
     ```

4. Clique em **Save** e depois em **Restart** na Function App.

> No código Python, a função usa essa configuração com `os.getenv("SQL_CONNECTION_STRING")` e o driver `pyodbc` para conectar ao banco.

---

## Clonando este repositório

No seu terminal (Bash, PowerShell, etc):

```bash
git clone https://github.com/NicolasRSJ/api-function-app-azure.git
cd api-function-app-azure
```

---

## (Opcional) Testar localmente

Se quiser rodar a Function na sua máquina antes de publicar:

1. Crie um ambiente virtual e instale as dependências (incluindo `pyodbc`, definido em `requirements.txt`):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # .venv\Scripts\activate   # Windows (PowerShell/CMD)

   pip install -r requirements.txt
   ```
2. (Opcional) Crie um arquivo local.settings.json (não commitado no Git) com a sua SQL_CONNECTION_STRING local, se quiser testar com o mesmo banco.
3. Inicie o host local das Functions:
  ```bash
   func start
   ```
5. Teste no navegador ou via ferramenta HTTP (Postman, Thunder Client, etc) em:
   ```h
   GET http://localhost:7071/api/usuarios
   ```

---

## Login no Azure via Terminal

No mesmo terminal:
  ```bash
   az login
   ```
Se você tiver mais de uma assinatura, opcionalmente selecione:
  ```bash
   az account set --subscription "NOME_OU_ID_DA_SUBSCRIPTION"
   ```

---

## Publicar a Function para o Azure

Dentro da pasta do projeto (api-function-app-azure), execute:
  ```bash
   func azure functionapp publish NOME_DA_FUNCTIONAPP --python
   ```
Exemplo:
  ```bash
   func azure functionapp publish apiusuarios-nicolas --python
   ```
O Core Tools vai:
- Criar um pacote com o código
- Fazer upload para a Function App no Azure
- Fazer o build remoto e atualizar a Function

---

## Testando a API publicada

Depois do deploy, sua Function ficará acessível em uma URL como:
  ```text
  https://NOME_DA_FUNCTIONAPP.azurewebsites.net
  ```
Os endpoints principais são:
### Listar Usuários
  ```http
  GET https://NOME_DA_FUNCTIONAPP.azurewebsites.net/api/usuarios
  ```
### Criar Usuários
  ```http
  POST https://NOME_DA_FUNCTIONAPP.azurewebsites.net/api/usuarios
  Content-Type: application/json
  ```
Exemplo:
  ```json
  {
     "nome": "Nicolas Rodrigues",
     "idade": 23,
     "email": "nicolas@gmail.com",
     "cidade": "Vitória"
   }
  ```
### Obter Usuários
  ```http
  GET https://NOME_DA_FUNCTIONAPP.azurewebsites.net/api/usuarios/1
  ```
### Atualizar Usuário
  ```http
  PUT https://NOME_DA_FUNCTIONAPP.azurewebsites.net/api/usuarios/1
  Content-Type: application/json
  ```
Exemplo:
  ```json
  {
     "nome": "Nicolas Rodrigues da Silva de Jesus",
     "idade": 23,
     "email": "nicolas@gmail.com",
     "cidade": "Vitória/ES"
   }
  ```
### Remover Usuário
  ```http
  DELETE https://NOME_DA_FUNCTIONAPP.azurewebsites.net/api/usuarios/1
  ```

---

## Opcional: CORS

Se for consumir a API de um front-end hospedado em outro domínio, você pode liberar CORS com:
  ```bash
   az functionapp cors add --name NOME_DA_FUNCTIONAPP --resource-group NOME_DO_RESOURCE_GROUP --allowed-origins "*"
   ```

---

## Observações Adicionais
- Os dados de usuários agora são armazenados em um Azure SQL Database na tabela `Usuarios`, e não mais apenas em memória.
- A conexão com o banco é feita via `pyodbc` usando a connection string armazenada no App Setting `SQL_CONNECTION_STRING`.
- Este projeto foi desenvolvido para fins de aula/demonstração de Azure Functions com Python, integração com Azure SQL e publicação via `func azure functionapp publish`.
