# Usuários

## POST /cadastro

Cadastra um novo usuário no sistema.

### Request Body

```json
{
  "username": "string",
  "nome": "string",
  "sobrenome": "string",
  "numero": 0,
  "email": "string",
  "telefone": 0,
  "endereco": "string",
  "ponto_referencia": "string (opcional)",
  "password": "string"
}
```

### Respostas

#### 200 - Cadastro realizado com sucesso

```json
{
  "success": true,
  "usuario_id": 1
}
```

#### 400 - Usuário ou email já cadastrado

```json
{
  "detail": "Usuário ou Email já cadastrado"
}
```

#### 422 - Erro de validação

Retornado quando campos obrigatórios estão ausentes ou com tipo incorreto.

```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

### Exemplos curl

Cadastro completo:

```bash
curl -X POST http://localhost:8000/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joaosilva",
    "nome": "João",
    "sobrenome": "Silva",
    "numero": 123,
    "email": "joao@email.com",
    "telefone": 11999998888,
    "endereco": "Rua das Flores",
    "ponto_referencia": "Próximo ao mercado",
    "password": "123456"
  }'
```

Cadastro sem ponto de referência:

```bash
curl -X POST http://localhost:8000/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria01",
    "nome": "Maria",
    "sobrenome": "Santos",
    "numero": 456,
    "email": "maria@email.com",
    "telefone": 11988887777,
    "endereco": "Av. Brasil",
    "password": "senha123"
  }'
```

Tentativa com username já existente:

```bash
curl -X POST http://localhost:8000/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "username": "joaosilva",
    "nome": "Outro",
    "sobrenome": "Usuário",
    "numero": 789,
    "email": "outro@email.com",
    "telefone": 11977776666,
    "endereco": "Rua Nova",
    "password": "abc123"
  }'
```

---

## GET /usuarios/{usuario_id}

Retorna os dados de um usuário pelo ID.

### Parâmetros de URL

| Parâmetro | Tipo | Descrição |
|---|---|---|
| usuario_id | int | ID do usuário |

### Respostas

#### 200 - Usuário encontrado

```json
{
  "id": 1,
  "nome_exibicao": "João Silva",
  "primeiro_nome": "João",
  "nome": "João",
  "sobrenome": "Silva",
  "email": "joao@email.com",
  "endereco": "Rua das Flores",
  "rua": "Rua das Flores",
  "numero": "123",
  "ponto_referencia": "Próximo ao mercado",
  "telefone": "11999998888",
  "foto_url": null
}
```

Quando o número do endereço é 0 ou nulo, retorna `"S/N"`.

#### 404 - Usuário não encontrado

```json
{
  "detail": "Usuário não encontrado"
}
```

#### 422 - Erro de validação

Retornado quando `usuario_id` não é um inteiro válido.

### Exemplos curl

Buscar usuário existente:

```bash
curl http://localhost:8000/usuarios/1
```

Buscar usuário inexistente:

```bash
curl http://localhost:8000/usuarios/9999
```
