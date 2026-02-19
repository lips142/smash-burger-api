# Autenticação

## POST /login

Realiza o login do usuário por **username** ou **email**.

### Request Body

```json
{
  "login": "string (username ou email)",
  "password": "string"
}
```

Também aceita o campo `username` no lugar de `login`:

```json
{
  "username": "string",
  "password": "string"
}
```

Se ambos `login` e `username` forem enviados, `login` tem prioridade.

### Respostas

#### 200 - Login realizado com sucesso

```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "usuario_id": 1
}
```

#### 401 - Credenciais inválidas

```json
{
  "detail": "Login ou senha inválidos"
}
```

#### 422 - Erro de validação

Retornado quando o body não segue o schema esperado (ex: campo `password` ausente).

```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Field required",
      "type": "missing"
    }
  ]
}
```

### Exemplos curl

Login com username:

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"login": "joaosilva", "password": "123456"}'
```

Login com email:

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"login": "joao@email.com", "password": "123456"}'
```

Login usando campo `username`:

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "joaosilva", "password": "123456"}'
```

Login com credenciais inválidas:

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"login": "inexistente", "password": "errada"}'
```
