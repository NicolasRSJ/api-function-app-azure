# API de Usuários com Azure Functions (Python)

Este projeto contém uma **API HTTP em Azure Functions (Python)** para cadastro e gerenciamento de usuários.  
Ela expõe endpoints para **listar, criar, atualizar e remover** usuários via HTTP.

---

## Pré-requisitos

Antes de usar este repositório, você precisa ter:

- Uma conta no **Microsoft Azure**
- Uma **Function App** criada no Azure (runtime **Python**)
- **Git** instalado
- **Azure Functions Core Tools** instalado (`func`)
- **Azure CLI** instalado (`az`)

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
   - **Version**: 3.12 (ex: `3.10`)
   - **Region**: região de sua preferência
4. Avance com **Next** até o final e clique em **Create**.
5. Aguarde o deploy terminar.

> Guarde o **nome da Function App**, vamos usar ele no comando de publicação:
> `NOME_DA_FUNCTIONAPP` (ex: `apiusuarios-nicolas`).

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

1. Crie um ambiente virtual e instale as dependências (se existir requirements.txt):
   ```bash
      python -m venv .venv
      source .venv/bin/activate  # Linux/macOS
      # .venv\Scripts\activate   # Windows (PowerShell/CMD)

      pip install -r requirements.txt
    ```
2. Inicie o host local das Functions:
   ```bash
      func start
    ```
3. Teste no navegador ou via ferramenta HTTP (Postman, Thunder Client, etc) em:
   - GET http://localhost:7071/api/usuarios

---

## Login no Azure pelo terminal

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
Depois do deploy, sua Function  ficará acessível em uma URL como:
```text
https://NOME_DA_FUNCTIONAPP.azurewebsites.net
```
Os endpoints principais são:
### Listas Usuários:
```http
GET https://NOME_DA_FUNCTIONAPP.azurewebsites.net/api/usuarios
```
### Criar Usuários:
```http
POST https://NOME_DA_FUNCTIONAPP.azurewebsites.net/api/usuarios
Content-Type: application/json
```
Body de exemplo:
```json
{
  "nome": "Nicolas Rodrigues",
  "idade": 23,
  "email": "nicolas@gmail.com",
  "cidade": "Vitória"
}
```
### Obter usuário por ID:
```http
GET https://NOME_DA_FUNCTIONAPP.azurewebsites.net/api/usuarios/1
```
### Atualizar Usuário:
```http
PUT https://NOME_DA_FUNCTIONAPP.azurewebsites.net/api/usuarios/1
Content-Type: application/json
```
Body de exemplo:
```json
{
  "nome": "Nicolas Rodrigues da Silva de Jesus",
  "idade": 23,
  "email": "nicolas@gmail.com",
  "cidade": "Vitória/ES"
}
```
### Remover Usuário:
```http
DELETE https://NOME_DA_FUNCTIONAPP.azurewebsites.net/api/usuarios/1
```

---

## CORS (acesso pelo navegador)
Se for consumir a API de um front-end hospedado em outro domínio, você pode liberar CORS com:
```bash
az functions cors add --name NOME_DA_FUNCTIONAPP --resource-group NOME_DO_RESOURCE_GROUP --allowed-origins "*"
```
**OBS:** Em produção, é ideal trocar o "*" pelo domínio específico do seu front-end.

---

## Observações Adicionais
- Os dados de usuários são armazenados em memória (um dicionário Python). Ao reiniciar a Function, os dados são perdidos — ideal para estudo e demonstração.
- Este projeto foi desenvolvido para fins de aula/demonstração de Azure Functions com Python.
