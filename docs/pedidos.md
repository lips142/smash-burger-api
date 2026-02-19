# Pedidos

## POST /pedidos

Cria um novo pedido com itens. O endereço de entrega é copiado automaticamente do cadastro do usuário.

### Request Body

```json
{
  "usuario_id": 1,
  "total": 57.80,
  "status": "Novo pedido",
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 2,
      "preco": 28.90
    }
  ]
}
```

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| usuario_id | int | sim | ID do usuário que faz o pedido |
| total | float | sim | Valor total do pedido |
| status | string | não | Default: "Novo pedido" |
| itens | array | não | Lista de itens do pedido |
| itens[].produto_id | int | sim | ID do produto |
| itens[].quantidade | int | sim | Quantidade |
| itens[].preco | float | sim | Preço unitário |

### Respostas

#### 200 - Pedido criado com sucesso

```json
{
  "success": true,
  "message": "Pedido criado",
  "id": 10
}
```

#### 404 - Usuário não encontrado

```json
{
  "detail": "Usuário não encontrado"
}
```

#### 400 - Erro na criação

```json
{
  "detail": "mensagem de erro"
}
```

#### 422 - Erro de validação

Retornado quando o body não segue o schema esperado.

### Exemplos curl

Criar pedido com itens:

```bash
curl -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 1,
    "total": 57.80,
    "itens": [
      {"produto_id": 1, "quantidade": 2, "preco": 28.90}
    ]
  }'
```

Criar pedido sem itens:

```bash
curl -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": 1, "total": 28.90}'
```

Criar pedido com usuário inexistente:

```bash
curl -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": 9999, "total": 10.00}'
```

---

## GET /pedidos

Lista todos os pedidos do sistema, ordenados por data (mais recente primeiro). Visão administrativa.

### Parâmetros

Nenhum.

### Respostas

#### 200 - Lista de pedidos

```json
[
  {
    "id": 10,
    "usuario_nome": "João Silva",
    "total": 57.80,
    "status": "Novo pedido",
    "data": "2026-02-19T12:30:00",
    "rua": "Rua das Flores",
    "numero": "123",
    "ponto_referencia": "Próximo ao mercado"
  }
]
```

Retorna lista vazia `[]` quando não há pedidos.

### Exemplos curl

Listar todos os pedidos:

```bash
curl http://localhost:8000/pedidos
```

---

## GET /pedidos/usuario/{usuario_id}

Lista os pedidos de um usuário específico, ordenados por data (mais recente primeiro).

### Parâmetros de URL

| Parâmetro | Tipo | Descrição |
|---|---|---|
| usuario_id | int | ID do usuário |

### Respostas

#### 200 - Pedidos do usuário

```json
[
  {
    "id": 10,
    "total": 57.80,
    "status": "Novo pedido",
    "data": "2026-02-19T09:30:00",
    "rua": "Rua das Flores",
    "numero": "123"
  }
]
```

Retorna lista vazia `[]` quando o usuário não tem pedidos.

#### 422 - Erro de validação

Retornado quando `usuario_id` não é um inteiro válido.

### Exemplos curl

Listar pedidos do usuário 1:

```bash
curl http://localhost:8000/pedidos/usuario/1
```

Listar pedidos de usuário sem pedidos:

```bash
curl http://localhost:8000/pedidos/usuario/9999
```

---

## GET /pedidos/{pedido_id}/itens

Retorna os itens de um pedido específico, com nome e imagem do produto.

### Parâmetros de URL

| Parâmetro | Tipo | Descrição |
|---|---|---|
| pedido_id | int | ID do pedido |

### Respostas

#### 200 - Itens do pedido

```json
[
  {
    "id": 1,
    "nome": "Bacon Smash",
    "imagem": "/static/images/bacon_smash.png",
    "quantidade": 2,
    "preco": 28.90
  }
]
```

Retorna lista vazia `[]` quando o pedido não tem itens ou não existe.

#### 422 - Erro de validação

Retornado quando `pedido_id` não é um inteiro válido.

### Exemplos curl

Buscar itens do pedido 10:

```bash
curl http://localhost:8000/pedidos/10/itens
```

Buscar itens de pedido inexistente:

```bash
curl http://localhost:8000/pedidos/9999/itens
```

---

## PUT /pedidos/{pedido_id}/status

Atualiza o status de um pedido.

### Parâmetros de URL

| Parâmetro | Tipo | Descrição |
|---|---|---|
| pedido_id | int | ID do pedido |

### Query Parameters

| Parâmetro | Tipo | Descrição |
|---|---|---|
| status | string | Novo status do pedido |

Valores comuns de status: `Novo pedido`, `Preparando`, `Enviado`, `Finalizado`.

### Respostas

#### 200 - Status atualizado

```json
{
  "success": true
}
```

#### 404 - Pedido não encontrado

```json
{
  "detail": "Pedido não encontrado"
}
```

#### 422 - Erro de validação

Retornado quando `pedido_id` não é um inteiro válido ou `status` está ausente.

### Exemplos curl

Atualizar status para "Preparando":

```bash
curl -X PUT "http://localhost:8000/pedidos/10/status?status=Preparando"
```

Atualizar status para "Enviado":

```bash
curl -X PUT "http://localhost:8000/pedidos/10/status?status=Enviado"
```

Atualizar status para "Finalizado":

```bash
curl -X PUT "http://localhost:8000/pedidos/10/status?status=Finalizado"
```

Atualizar pedido inexistente:

```bash
curl -X PUT "http://localhost:8000/pedidos/9999/status?status=Preparando"
```
