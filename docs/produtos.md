# Produtos

## GET /produtos

Retorna a lista completa de produtos cadastrados no banco de dados.

### Parâmetros

Nenhum.

### Respostas

#### 200 - Lista de produtos

```json
[
  {
    "id": 1,
    "nome": "Bacon Smash",
    "preco": 28.90,
    "imagem": "/static/images/bacon_smash.png",
    "descricao": "Hambúrguer smash com bacon crocante",
    "avaliacao": 4.8,
    "ingredientes": ["pão", "carne", "bacon", "queijo", "molho especial"],
    "categoria": "Hambúrgueres"
  },
  {
    "id": 2,
    "nome": "Coca-Cola",
    "preco": 7.00,
    "imagem": "/static/images/coca.png",
    "descricao": "Coca-Cola lata 350ml",
    "avaliacao": 4.5,
    "ingredientes": [],
    "categoria": "Bebidas"
  }
]
```

Retorna lista vazia `[]` quando não há produtos cadastrados.

#### 500 - Erro interno

Retornado em caso de falha na conexão com o banco de dados.

### Exemplos curl

Listar todos os produtos:

```bash
curl http://localhost:8000/produtos
```

Listar produtos com resposta formatada (jq):

```bash
curl -s http://localhost:8000/produtos | jq .
```
