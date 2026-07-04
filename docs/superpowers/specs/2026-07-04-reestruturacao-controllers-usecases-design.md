# Reestruturação: Controllers + Usecases

## Contexto

Hoje toda a API vive em `app/main.py` (rotas + regra de negócio juntas) e
`app/models.py` mistura tabelas SQLAlchemy com schemas Pydantic. Objetivo:
separar por domínio em `controller` (rota) + `usecase` (regra de negócio),
mantendo estrutura simples e segura para iniciante.

## Domínios identificados

Baseado nas rotas existentes e em `docs/*.md` (auth, produtos, usuarios, pedidos):

- **auth**: `POST /login`
- **produtos**: `GET /produtos`
- **usuarios**: `GET /usuarios/{id}`, `POST /usuarios/{id}`
- **pedidos**: `POST /pedidos`, `GET /pedidos`, `GET /pedidos/{id}/itens`,
  `GET /pedidos/usuario/{id}`, `PUT /pedidos/{id}/status`

## Decisões

1. **Sem camada de repository.** Usecase acessa `Session` do SQLAlchemy
   diretamente. Menos arquivos, mais fácil de acompanhar o fluxo completo
   pra quem tá começando.
2. **`models.py` fica só com tabelas SQLAlchemy** (um arquivo único,
   evita depender de relationship cruzada entre pastas — `Pedido` referencia
   `Produto` e `Usuario`). Schemas Pydantic (request/response) vão para
   `schemas.py` de cada domínio.

## Estrutura de pastas

```
app/
  main.py              # cria app, middlewares, monta static, include_router dos módulos
  database.py          # inalterado
  models.py            # só tabelas SQLAlchemy: ProdutoDB, UsuarioDB, PedidoDB, ItemPedidoDB, CarrinhoDB
  dependencies.py       # get_db() compartilhado
  utils.py              # obter_hora_brasil() e helpers compartilhados
  modules/
    auth/
      controller.py     # APIRouter: POST /login
      usecase.py        # autenticar_usuario(...)
      schemas.py         # LoginData
    produtos/
      controller.py     # APIRouter: GET /produtos
      usecase.py        # listar_produtos(...)
      schemas.py         # Produto, ProdutoCreate
    usuarios/
      controller.py     # APIRouter: GET/POST /usuarios/{id}
      usecase.py        # obter_usuario(...), atualizar_usuario(...)
      schemas.py         # Usuario, UsuarioCreate
    pedidos/
      controller.py     # APIRouter: rotas de pedido
      usecase.py        # criar_pedido, listar_pedidos, listar_itens_pedido,
                          # listar_pedidos_usuario, atualizar_status_pedido
      schemas.py         # Pedido, PedidoCreate, ItemPedido, ItemPedidoCreate
```

Scripts utilitários fora do app (`popular_db.py`, `test_db.py`,
`app/create_tables.py`) permanecem como estão — não fazem parte da API.

## Fluxo de uma requisição

`controller.py` (recebe request, injeta `Session` via `Depends(get_db)`,
chama usecase, traduz erro pra `HTTPException`) → `usecase.py` (regra de
negócio pura, recebe `Session` e dados já validados, faz query/commit) →
`models.py` (tabela).

## Erros

Mantém o padrão atual: usecase levanta `Exception`/faz `rollback` quando
aplicável; controller decide o `HTTPException` (404/400/401) — igual ao
comportamento hoje, só movido de lugar.

## Fora de escopo

- Sem mudança de comportamento/contrato das rotas (mesmos paths, métodos,
  request/response).
- Sem testes automatizados novos (projeto não tem hoje).
- Sem repository layer (decidido acima).
- `CarrinhoDB` existe no banco mas não tem rota hoje — só migra a tabela,
  sem criar módulo `carrinho`.
