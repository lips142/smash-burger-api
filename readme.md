# Smash Burguer API

API RESTful desenvolvida com FastAPI para gerenciamento de pedidos de uma hamburgueria digital. Projetada para atender aplicações mobile (Flutter), web e painel administrativo.

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI |
| Linguagem | Python |
| Banco de Dados | PostgreSQL |
| ORM | SQLAlchemy |
| Validação | Pydantic |
| Documentação | Swagger / OpenAPI |
| Arquivos Estáticos | FastAPI StaticFiles |
| CORS | Habilitado (todas as origens) |

## Estrutura do Projeto

```
smash-burger-api/
├── app/
│   ├── main.py            # Aplicação FastAPI e todos os endpoints
│   ├── database.py        # Conexão com PostgreSQL (SQLAlchemy)
│   ├── models.py          # Modelos SQLAlchemy e schemas Pydantic
│   ├── create_tables.py   # Script de criação das tabelas
│   ├── routes.py          # (não integrado)
│   ├── produtos.py        # (não integrado)
│   ├── pedidos.py         # (não integrado)
│   └── carrinho.py        # (não integrado)
├── static/
│   ├── images/            # Imagens dos produtos
│   └── index.html
├── docs/                  # Documentação dos endpoints
├── popular_db.py          # Script para popular o banco com produtos
└── test_db.py             # Teste de conexão com o banco
```

## Modelo de Dados

### Usuario

| Campo | Tipo | Observação |
|---|---|---|
| id | Integer | PK, auto-increment |
| username | String | único, obrigatório |
| nome | String | obrigatório |
| sobrenome | String | obrigatório |
| email | String | único, obrigatório |
| telefone | String | opcional |
| endereco | String | opcional |
| numero | Integer | número do endereço |
| ponto_referencia | String | opcional |
| password | String | obrigatório |
| foto_url | String | opcional |

### Produto

| Campo | Tipo | Observação |
|---|---|---|
| id | Integer | PK, auto-increment |
| nome | String | obrigatório |
| preco | Float | obrigatório |
| imagem | String | URL da imagem |
| descricao | String | obrigatório |
| avaliacao | Float | nota do produto |
| ingredientes | JSON | lista de ingredientes |
| categoria | String | obrigatório |

### Pedido

| Campo | Tipo | Observação |
|---|---|---|
| id | Integer | PK, auto-increment |
| usuario_id | Integer | FK → usuarios.id |
| total | Numeric(10,2) | valor total |
| data | DateTime | horário de Brasília |
| status | String | default: "Pedido aceito" |
| rua_entrega | String | copiado do endereço do usuário |
| numero_entrega | String | copiado do número do usuário |
| ponto_referencia | String | copiado do ponto de referência |

### ItemPedido

| Campo | Tipo | Observação |
|---|---|---|
| id | Integer | PK, auto-increment |
| pedido_id | Integer | FK → pedidos.id |
| produto_id | Integer | FK → produtos.id |
| quantidade | Integer | — |
| preco | Float | preço unitário no momento do pedido |

### Relacionamentos

- 1 Usuário → N Pedidos
- 1 Pedido → N ItensPedido
- 1 Produto → N ItensPedido

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| POST | `/login` | Login por username ou email |
| POST | `/cadastro` | Cadastro de usuário |
| GET | `/usuarios/{usuario_id}` | Dados do usuário |
| GET | `/produtos` | Listar todos os produtos |
| POST | `/pedidos` | Criar pedido com itens |
| GET | `/pedidos` | Listar todos os pedidos (admin) |
| GET | `/pedidos/usuario/{usuario_id}` | Pedidos de um usuário |
| GET | `/pedidos/{pedido_id}/itens` | Itens de um pedido |
| PUT | `/pedidos/{pedido_id}/status` | Atualizar status do pedido |

Documentação detalhada com exemplos curl: [docs/](docs/)

## Arquivos Estáticos

Imagens dos produtos são servidas em `/static/images/`.

Exemplo: `http://localhost:8000/static/images/bacon_smash.png`

## Como Executar

### 1. Clonar o repositório

```bash
git clone https://github.com/lips142/smash-burguer-api.git
cd smash-burguer-api
```

### 2. Criar e ativar ambiente virtual

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install fastapi uvicorn sqlalchemy psycopg2
```

### 4. Configurar banco de dados

No arquivo `app/database.py`, ajuste a connection string:

```python
DATABASE_URL = "postgresql://smashuser:123@localhost:5432/smashdb"
```

### 5. Criar tabelas

```bash
python app/create_tables.py
```

### 6. Popular banco (opcional)

```bash
python popular_db.py
```

### 7. Rodar a aplicação

```bash
uvicorn app.main:app --reload
```

Acesse a documentação interativa em: http://localhost:8000/docs

## Fluxo de Pedido

1. Usuário realiza login (`POST /login`)
2. Consulta produtos (`GET /produtos`)
3. Envia pedido com itens (`POST /pedidos`)
4. API calcula e salva com status "Novo pedido"
5. Status pode ser atualizado para: Preparando, Enviado, Finalizado (`PUT /pedidos/{id}/status`)

## Autor

Felipe Luz — Backend Developer | Python | FastAPI
