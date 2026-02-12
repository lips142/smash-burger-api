# Smash Burguer API
API RESTful desenvolvida com FastAPI para gerenciamento completo de pedidos de uma hamburgueria digital.

Projetada para atender aplicações mobile, web e painel administrativo, com foco em organização modular,
 clareza arquitetural e facilidade de manutenção.

# Sobre o Projeto

A Smash Burguer API foi criada para atender um aplicativo mobile de pedidos de hambúrguer.
Ela fornece endpoints para:

- Autenticação de usuários

- Cadastro e consulta de usuários

- Gerenciamento de produtos

- Criação e acompanhamento de pedidos

- Consulta de itens do pedido

- Servir imagens estáticas dos produtos

O foco da API é oferecer uma estrutura REST organizada, clara e fácil de consumir por aplicações frontend.



#Arquitetura


Camada	                      Tecnologia

Backend	                       FastAPI
Linguagem	                Python
Banco de Dados	              PostgreSQL
ORM	                      SQLAlchemy
Validação	               Pydantic
Documentação	           Swagger / OpenAPI
Arquivos Estáticos	   FastAPI StaticFiles
CORS	                       Habilitado

# Arquitetura em Camadas
- Cliente (Flutter/Web)
        ↓
- FastAPI (Rotas)
        ↓
- Camada de Serviços
        ↓
- SQLAlchemy ORM
        ↓
- PostgreSQL


# Separação clara de responsabilidades:

routes.py → Registro das rotas

produtos.py, pedidos.py, carrinho.py → Regras específicas

models.py → Estrutura do banco

database.py → Conexão com PostgreSQL

Isso demonstra boa prática de organização modular.

# Estrutura do Projeto


fastapi-api/
│
├── app/
│   ├── main.py            # Inicialização da aplicação
│   ├── database.py        # Configuração da conexão PostgreSQL
│   ├── models.py          # Modelos SQLAlchemy
│   ├── produtos.py        # Endpoints de produtos
│   ├── pedidos.py         # Endpoints de pedidos
│   ├── carrinho.py        # Lógica de carrinho
│   ├── routes.py          # Registro central de rotas
│   ├── create_tables.py   # Script de criação das tabelas
│
├── static/
│   ├── images/            # Imagens dos produtos
│   └── index.html
│
├── popular_db.py          # Script para popular banco
├── test_db.py             # Teste de conexão
└── venv/



# Modelo de Dados
# Entidades Principais

# Usuario

-  id

- nome

- email

- senha

# Produto

- id

- nome

- descricao

- preco

- imagem

# ingredientes (JSON)

- Pedido

- id

- usuario_id

- status

- total

# ItemPedido

- id

- pedido_id

- produto_id

- quantidade


# Como Executar o Projeto

Clonar o repositório
git clone https://github.com/seu-usuario/smash-burguer-api.git
cd smash-burguer-api



# Ativar ambiente

Windows:

venv\Scripts\activate


Linux/macOS:

source venv/bin/activate


# Instalar dependências
pip install fastapi uvicorn sqlalchemy psycopg2


# Configurar banco

No arquivo database.py:

DATABASE_URL = "postgresql://usuario:senha@localhost:5432/smashdb"


# Criar tabelas
python app/create_tables.py


# Popular banco (opcional)

python popular_db.py


# Rodar aplicação

uvicorn app.main:app --reload

Acesse:

http://localhost:8000/docs




# Principais Endpoints
# Autenticação

POST /login

#Usuários

POST /cadastro

GET /usuarios/{usuario_id}

# Produtos

GET /produtos

GET /produtos/{produto_id}

POST /produtos

DELETE /produtos/{produto_id}

# Pedidos

POST /pedidos

GET /pedidos

GET /pedidos/usuario/{usuario_id}

GET /pedidos/{pedido_id}/itens

PUT /pedidos/{pedido_id}/status


# A API utiliza relacionamento entre:

1 Usuário → N Pedidos

1 Pedido → N Itens

1 Produto → N ItensPedido

Ingredientes são armazenados em formato JSON.



# Arquivos Estáticos

Imagens são servidas via:

/static/images/

Exemplo:

http://localhost:8000/static/images/bacon_smash.png


# Público-Alvo

Aplicação Mobile (Flutter)

Frontend Web

Painel administrativo de pedidos



# Fluxo Completo de Pedido

Usuário realiza login

Consulta produtos

Adiciona itens ao carrinho

Envia requisição POST /pedidos

API calcula total

Pedido é criado com status PENDENTE

Status pode ser atualizado para PREPARANDO, ENVIADO, FINALIZADO


# Tratamento de Erros

# A API utiliza:

HTTPException para erros de negócio

Validação automática via Pydantic

Códigos HTTP padronizados

Código	Significado
400	Requisição inválida
401	Não autorizado
404	Recurso não encontrado
500	Erro interno


# Segurança

Validação de dados com Pydantic

Separação de camadas

Uso de ORM para evitar SQL Injection



# Testes

O projeto inclui:

test_db.py
Para validação da conexão com banco.


# Decisões de Design
✔ Modularização

Separação por domínio (produtos, pedidos, carrinho).

✔ Uso de ORM

Facilita manutenção e reduz risco de SQL Injection.

✔ Ingredientes em JSON

Flexibilidade para composição dinâmica de produtos.



# Possíveis Melhorias Futuras

Implementar JWT

Implementar Docker

Criar testes automatizados (pytest)

Implementar cache (Redis)

Implementar CI/CD

Deploy em ambiente cloud


Autor

Felipe Luz
Backend Developer | Python | FastAPI 