# Reestruturação Controllers + Usecases Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Separar `app/main.py` (hoje com todas as rotas e regra de negócio) em módulos por domínio (`auth`, `produtos`, `usuarios`, `pedidos`), cada um com `controller.py` (rota) + `usecase.py` (regra de negócio) + `schemas.py` (Pydantic), sem mudar nenhum contrato de rota existente.

**Architecture:** Camadas: `controller` (FastAPI `APIRouter`, injeta `Session` via `Depends(get_db)`, chama `usecase`) → `usecase` (função pura que recebe `Session` + dados já validados, faz query/commit) → `models` (tabelas SQLAlchemy). Sem repository (decidido na spec).

**Tech Stack:** FastAPI 0.139, SQLAlchemy 2.0, Pydantic 2.13, PostgreSQL (via `docker-compose.yml`), uvicorn.

## Global Constraints

- Sem testes automatizados novos — projeto não tem hoje e spec exclui isso do escopo. Verificação é manual: subir o servidor e testar as rotas com `curl`.
- Sem mudança de contrato de rota: mesmos paths, métodos HTTP, request/response de hoje.
- Sem camada de repository — usecase usa `Session` do SQLAlchemy direto.
- Preservar comportamento exato, **inclusive bugs existentes**. Ex: em `criar_pedido`, o `except Exception` genérico captura até a `HTTPException(404)` levantada dentro do próprio try e a reconverte em 400 — isso é um bug pré-existente, não deve ser corrigido aqui (fora de escopo).
- `app/models.py` fica só com tabelas SQLAlchemy: `ProdutoDB`, `UsuarioDB`, `CarrinhoDB`, `ItemPedidoDB`, `PedidoDB`.
- `CarrinhoDB` não tem rota hoje — só a tabela continua em `models.py`, sem módulo `carrinho`.
- Migrar `app/main.py`'s `PedidoCreate`/`ItemPedidoCreate` (que tem `status: str = "Novo pedido"` como default, e é a versão realmente usada pela rota, pois sobrescreve a de `models.py` no próprio namespace de `main.py`) — não a versão duplicada de `models.py` (que não tinha default e nunca era usada).
- Banco sobe via `docker compose up -d db` (porta host `5433`). Antes de testar manualmente, copiar `.env.example` pra `.env` se ainda não existir (`.env.example` já aponta pra porta `5433`).

---

### Task 1: Infraestrutura compartilhada (`dependencies.py`, `utils.py`)

**Files:**
- Create: `app/dependencies.py`
- Create: `app/utils.py`
- Modify: `app/main.py`

**Interfaces:**
- Produces: `app.dependencies.get_db() -> Generator[Session, None, None]`, `app.utils.obter_hora_brasil() -> datetime.datetime`

- [ ] **Step 1: Criar `app/dependencies.py`**

```python
from app.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: Criar `app/utils.py`**

```python
from datetime import datetime, timedelta


def obter_hora_brasil():
    return datetime.utcnow() - timedelta(hours=3)
```

- [ ] **Step 3: Atualizar `app/main.py` pra usar os dois novos módulos**

Remover de `app/main.py` a função `get_db()` (linhas 25-30) e `obter_hora_brasil()` (linhas 32-33), e trocar o import:

```python
from app.dependencies import get_db
from app.utils import obter_hora_brasil
```

`app/main.py` deve continuar exatamente com o mesmo comportamento — só a definição de `get_db`/`obter_hora_brasil` que muda de lugar.

- [ ] **Step 4: Rodar app e verificar que nada quebrou**

```bash
docker compose up -d db
[ -f .env ] || cp .env.example .env
uvicorn app.main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/produtos | head -c 200
kill %1
```

Esperado: resposta JSON com lista de produtos (ou `[]` se banco vazio), sem erro de import.

- [ ] **Step 5: Commit**

```bash
git add app/dependencies.py app/utils.py app/main.py
git commit -m "refactor: extrai get_db e obter_hora_brasil pra módulos compartilhados"
```

---

### Task 2: Módulo `auth`

**Files:**
- Create: `app/modules/__init__.py`
- Create: `app/modules/auth/__init__.py`
- Create: `app/modules/auth/schemas.py`
- Create: `app/modules/auth/usecase.py`
- Create: `app/modules/auth/controller.py`
- Modify: `app/main.py`

**Interfaces:**
- Consumes: `app.dependencies.get_db` (Task 1)
- Produces: `app.modules.auth.usecase.autenticar_usuario(db: Session, login_value: str, password: str) -> dict`, `app.modules.auth.controller.router` (APIRouter)

- [ ] **Step 1: Criar pacotes vazios**

```bash
mkdir -p app/modules/auth
touch app/modules/__init__.py app/modules/auth/__init__.py
```

- [ ] **Step 2: Criar `app/modules/auth/schemas.py`**

```python
from typing import Optional

from pydantic import BaseModel


class LoginData(BaseModel):
    login: Optional[str] = None
    username: Optional[str] = None
    password: str
```

- [ ] **Step 3: Criar `app/modules/auth/usecase.py`**

```python
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models


def autenticar_usuario(db: Session, login_value: str, password: str):
    user = db.query(models.UsuarioDB).filter(
        (models.UsuarioDB.username == login_value) |
        (models.UsuarioDB.email == login_value)
    ).first()

    if user and user.password == password:
        return {"success": True, "usuario_id": user.id, "message": "Login realizado com sucesso"}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")
```

- [ ] **Step 4: Criar `app/modules/auth/controller.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.modules.auth import usecase
from app.modules.auth.schemas import LoginData

router = APIRouter()


@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    login_value = data.login or data.username
    return usecase.autenticar_usuario(db, login_value, data.password)
```

- [ ] **Step 5: Atualizar `app/main.py`**

Remover a classe `LoginData` e a rota `@app.post("/login")` de `app/main.py`. Adicionar:

```python
from app.modules.auth.controller import router as auth_router
```

E, após a criação de `app`/middleware/static mount:

```python
app.include_router(auth_router)
```

- [ ] **Step 6: Verificar manualmente**

```bash
docker compose up -d db
uvicorn app.main:app --port 8000 &
sleep 2
curl -s -X POST http://localhost:8000/login -H "Content-Type: application/json" -d '{"login":"nao-existe","password":"x"}'
kill %1
```

Esperado: `{"detail":"Credenciais inválidas"}` com status 401 (rota responde, sem erro 500/import).

- [ ] **Step 7: Commit**

```bash
git add app/modules/__init__.py app/modules/auth app/main.py
git commit -m "refactor: extrai modulo auth (controller/usecase/schemas)"
```

---

### Task 3: Módulo `produtos`

**Files:**
- Create: `app/modules/produtos/__init__.py`
- Create: `app/modules/produtos/schemas.py`
- Create: `app/modules/produtos/usecase.py`
- Create: `app/modules/produtos/controller.py`
- Modify: `app/main.py`

**Interfaces:**
- Consumes: `app.dependencies.get_db` (Task 1)
- Produces: `app.modules.produtos.usecase.listar_produtos(db: Session) -> list[models.ProdutoDB]`, `app.modules.produtos.controller.router`

- [ ] **Step 1: Criar pacote**

```bash
mkdir -p app/modules/produtos
touch app/modules/produtos/__init__.py
```

- [ ] **Step 2: Criar `app/modules/produtos/schemas.py`**

```python
from typing import List, Optional

from pydantic import BaseModel


class Produto(BaseModel):
    id: int
    nome: str
    preco: float
    imagem: Optional[str] = None
    descricao: Optional[str] = None
    avaliacao: Optional[float] = None
    ingredientes: Optional[List[str]] = None
    categoria: str

    class Config:
        from_attributes = True


class ProdutoCreate(BaseModel):
    nome: str
    preco: float
    imagem: Optional[str] = None
    descricao: Optional[str] = None
    avaliacao: Optional[float] = None
    ingredientes: Optional[List[str]] = None
    categoria: str
```

- [ ] **Step 3: Criar `app/modules/produtos/usecase.py`**

```python
from sqlalchemy.orm import Session

from app import models


def listar_produtos(db: Session):
    return db.query(models.ProdutoDB).all()
```

- [ ] **Step 4: Criar `app/modules/produtos/controller.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.modules.produtos import usecase

router = APIRouter()


@router.get("/produtos")
def listar_produtos(db: Session = Depends(get_db)):
    return usecase.listar_produtos(db)
```

- [ ] **Step 5: Atualizar `app/main.py`**

Remover a rota `@app.get("/produtos")` de `app/main.py`. Adicionar:

```python
from app.modules.produtos.controller import router as produtos_router
```

```python
app.include_router(produtos_router)
```

- [ ] **Step 6: Verificar manualmente**

```bash
docker compose up -d db
uvicorn app.main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/produtos
kill %1
```

Esperado: mesma lista de produtos de antes (JSON array).

- [ ] **Step 7: Commit**

```bash
git add app/modules/produtos app/main.py
git commit -m "refactor: extrai modulo produtos (controller/usecase/schemas)"
```

---

### Task 4: Módulo `usuarios`

**Files:**
- Create: `app/modules/usuarios/__init__.py`
- Create: `app/modules/usuarios/schemas.py`
- Create: `app/modules/usuarios/usecase.py`
- Create: `app/modules/usuarios/controller.py`
- Modify: `app/main.py`

**Interfaces:**
- Consumes: `app.dependencies.get_db` (Task 1)
- Produces: `app.modules.usuarios.usecase.obter_usuario(db: Session, usuario_id: int) -> models.UsuarioDB`, `app.modules.usuarios.usecase.atualizar_usuario(db: Session, usuario_id: int, nome: str, sobrenome: str, endereco: str, ponto_referencia: str, telefone: str, foto_bytes: Optional[bytes]) -> models.UsuarioDB`, `app.modules.usuarios.controller.router`

- [ ] **Step 1: Criar pacote**

```bash
mkdir -p app/modules/usuarios
touch app/modules/usuarios/__init__.py
```

- [ ] **Step 2: Criar `app/modules/usuarios/schemas.py`**

```python
from typing import Optional

from pydantic import BaseModel


class Usuario(BaseModel):
    id: int
    username: str
    nome: str
    sobrenome: str
    email: str
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    ponto_referencia: Optional[str] = None

    class Config:
        from_attributes = True


class UsuarioCreate(BaseModel):
    username: str
    email: str
    password: str
```

- [ ] **Step 3: Criar `app/modules/usuarios/usecase.py`**

```python
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models


def obter_usuario(db: Session, usuario_id: int):
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


def atualizar_usuario(
    db: Session,
    usuario_id: int,
    nome: str,
    sobrenome: str,
    endereco: str,
    ponto_referencia: str,
    telefone: str,
    foto_bytes: Optional[bytes],
):
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario.nome = nome
    usuario.sobrenome = sobrenome
    usuario.endereco = endereco
    usuario.ponto_referencia = ponto_referencia
    usuario.telefone = telefone

    if foto_bytes is not None:
        usuario.foto = foto_bytes

    db.commit()
    db.refresh(usuario)
    return usuario
```

- [ ] **Step 4: Criar `app/modules/usuarios/controller.py`**

```python
import base64

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.modules.usuarios import usecase

router = APIRouter()


@router.get("/usuarios/{usuario_id}")
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = usecase.obter_usuario(db, usuario_id)
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "sobrenome": usuario.sobrenome,
        "endereco": usuario.endereco,
        "ponto_referencia": usuario.ponto_referencia,
        "foto_bytes": base64.b64encode(usuario.foto).decode('utf-8') if usuario.foto else None,
        "email": usuario.email,
        "telefone": usuario.telefone,
    }


@router.post("/usuarios/{usuario_id}")
async def atualizar_usuario(
    usuario_id: int,
    nome: str = Form(...),
    sobrenome: str = Form(""),
    endereco: str = Form(""),
    ponto_referencia: str = Form(""),
    telefone: str = Form(""),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    foto_bytes = await file.read() if file else None
    usecase.atualizar_usuario(db, usuario_id, nome, sobrenome, endereco, ponto_referencia, telefone, foto_bytes)
    return {"success": True, "message": "Perfil atualizado com sucesso"}
```

- [ ] **Step 5: Atualizar `app/main.py`**

Remover as rotas `@app.get("/usuarios/{usuario_id}")` e `@app.post("/usuarios/{usuario_id}")` de `app/main.py`, junto com o import `base64` e `UploadFile, File, Form` (se não usados mais em `main.py`). Adicionar:

```python
from app.modules.usuarios.controller import router as usuarios_router
```

```python
app.include_router(usuarios_router)
```

- [ ] **Step 6: Verificar manualmente**

```bash
docker compose up -d db
uvicorn app.main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/usuarios/1
kill %1
```

Esperado: dados do usuário id 1 (ou `{"detail":"Usuário não encontrado"}` com 404 se não existir) — igual ao comportamento anterior.

- [ ] **Step 7: Commit**

```bash
git add app/modules/usuarios app/main.py
git commit -m "refactor: extrai modulo usuarios (controller/usecase/schemas)"
```

---

### Task 5: Módulo `pedidos`

**Files:**
- Create: `app/modules/pedidos/__init__.py`
- Create: `app/modules/pedidos/schemas.py`
- Create: `app/modules/pedidos/usecase.py`
- Create: `app/modules/pedidos/controller.py`
- Modify: `app/main.py`

**Interfaces:**
- Consumes: `app.dependencies.get_db` (Task 1), `app.utils.obter_hora_brasil` (Task 1)
- Produces: `app.modules.pedidos.usecase.criar_pedido`, `listar_todos_pedidos`, `listar_itens_pedido`, `listar_pedidos_usuario`, `atualizar_status_pedido` (assinaturas abaixo), `app.modules.pedidos.controller.router`

- [ ] **Step 1: Criar pacote**

```bash
mkdir -p app/modules/pedidos
touch app/modules/pedidos/__init__.py
```

- [ ] **Step 2: Criar `app/modules/pedidos/schemas.py`**

```python
import datetime
from typing import List, Optional

from pydantic import BaseModel


class ItemPedido(BaseModel):
    id: int
    pedido_id: int
    produto_id: int
    quantidade: int
    preco: float
    nome: Optional[str] = None
    imagem: Optional[str] = None

    class Config:
        from_attributes = True


class ItemPedidoCreate(BaseModel):
    produto_id: int
    quantidade: int
    preco: float


class Pedido(BaseModel):
    id: int
    usuario_id: int
    total: float
    data: datetime.datetime
    status: str
    itens: List[ItemPedido] = []
    previsao_entrega: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


class PedidoCreate(BaseModel):
    usuario_id: int
    total: float
    status: str = "Novo pedido"
    itens: List[ItemPedidoCreate] = []
```

Nota: `PedidoCreate.status` tem default `"Novo pedido"` — vem da versão que estava em `app/main.py` (a que a rota realmente usava), não da versão duplicada e não-usada de `app/models.py` (que não tinha default).

- [ ] **Step 3: Criar `app/modules/pedidos/usecase.py`**

```python
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app.modules.pedidos.schemas import PedidoCreate
from app.utils import obter_hora_brasil


def criar_pedido(db: Session, pedido: PedidoCreate):
    try:
        user = db.query(models.UsuarioDB).filter(models.UsuarioDB.id == pedido.usuario_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

        novo_pedido = models.PedidoDB(
            usuario_id=pedido.usuario_id,
            total=pedido.total,
            data=obter_hora_brasil(),
            status=pedido.status,
            rua_entrega=user.endereco,
            numero_entrega=str(getattr(user, 'numero', 'S/N')),
            ponto_referencia=user.ponto_referencia
        )
        db.add(novo_pedido)
        db.flush()

        for item in pedido.itens:
            item_db = models.ItemPedidoDB(
                pedido_id=novo_pedido.id,
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                preco=item.preco
            )
            db.add(item_db)

        db.commit()
        db.refresh(novo_pedido)
        return {"success": True, "id": novo_pedido.id}
    except Exception as e:
        db.rollback()
        print(f"ERRO AO SALVAR PEDIDO: {e}")
        raise HTTPException(status_code=400, detail=str(e))


def listar_todos_pedidos(db: Session):
    pedidos = db.query(models.PedidoDB).order_by(models.PedidoDB.data.desc()).all()
    resultado = []

    for p in pedidos:
        usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.id == p.usuario_id).first()
        nome_cliente = f"{usuario.nome} {usuario.sobrenome}" if usuario else "Cliente Desconhecido"

        resultado.append({
            "id": p.id,
            "usuario_nome": nome_cliente,
            "total": float(p.total),
            "status": p.status,
            "data": p.data.isoformat() if p.data else None,
            "rua": p.rua_entrega or "Não informada",
            "numero": p.numero_entrega or "S/N"
        })
    return resultado


def listar_itens_pedido(db: Session, pedido_id: int):
    itens = db.query(models.ItemPedidoDB).filter(models.ItemPedidoDB.pedido_id == pedido_id).all()

    resultado = []
    for item in itens:
        if not item.produto:
            resultado.append({
                "nome": "Produto indisponível",
                "quantidade": item.quantidade,
                "preco": float(item.preco),
                "imagem": None,
                "ingredientes": []
            })
            continue

        url_imagem = item.produto.imagem
        url_formatada = url_imagem.replace("10.0.2.2", "localhost") if url_imagem else None

        resultado.append({
            "nome": item.produto.nome,
            "quantidade": item.quantidade,
            "preco": float(item.preco),
            "imagem": url_formatada,
            "ingredientes": item.produto.ingredientes or []
        })
    return resultado


def listar_pedidos_usuario(db: Session, usuario_id: int):
    pedidos = db.query(models.PedidoDB).filter(models.PedidoDB.usuario_id == usuario_id).all()
    if not pedidos:
        return []
    return pedidos


def atualizar_status_pedido(db: Session, pedido_id: int, status: str):
    pedido = db.query(models.PedidoDB).filter(models.PedidoDB.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    pedido.status = status
    db.commit()
    db.refresh(pedido)
    return {"success": True, "status": pedido.status}
```

- [ ] **Step 4: Criar `app/modules/pedidos/controller.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.modules.pedidos import usecase
from app.modules.pedidos.schemas import PedidoCreate

router = APIRouter()


@router.post("/pedidos")
def criar_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    return usecase.criar_pedido(db, pedido)


@router.get("/pedidos")
def listar_todos_pedidos(db: Session = Depends(get_db)):
    return usecase.listar_todos_pedidos(db)


@router.get("/pedidos/{pedido_id}/itens")
def listar_itens_pedido(pedido_id: int, db: Session = Depends(get_db)):
    return usecase.listar_itens_pedido(db, pedido_id)


@router.get("/pedidos/usuario/{usuario_id}")
def listar_pedidos_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return usecase.listar_pedidos_usuario(db, usuario_id)


@router.put("/pedidos/{pedido_id}/status")
def atualizar_status_pedido(pedido_id: int, status: str, db: Session = Depends(get_db)):
    return usecase.atualizar_status_pedido(db, pedido_id, status)
```

- [ ] **Step 5: Atualizar `app/main.py`**

Remover de `app/main.py`: classes `ItemPedidoCreate`/`PedidoCreate` locais e todas as rotas `/pedidos*`. Adicionar:

```python
from app.modules.pedidos.controller import router as pedidos_router
```

```python
app.include_router(pedidos_router)
```

Depois deste passo, `app/main.py` deve conter só: criação do `app`, middleware CORS, mount do `/static` e os 4 `include_router`. Ele não deve mais importar `Depends`, `HTTPException`, `Session`, `models`, `List`, `Optional`, `BaseModel`, `datetime`/`timedelta`, `base64`, `UploadFile`/`File`/`Form` — tudo isso migrou pros módulos.

- [ ] **Step 6: Verificar manualmente**

```bash
docker compose up -d db
uvicorn app.main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/pedidos
kill %1
```

Esperado: lista de pedidos (JSON array, mesmo formato de antes).

- [ ] **Step 7: Commit**

```bash
git add app/modules/pedidos app/main.py
git commit -m "refactor: extrai modulo pedidos (controller/usecase/schemas)"
```

---

### Task 6: Reduzir `app/models.py` só pras tabelas SQLAlchemy

**Files:**
- Modify: `app/models.py`

**Interfaces:**
- Consumes: nenhuma (só remove código que já foi movido nas Tasks 2-5)
- Produces: `app.models.ProdutoDB`, `UsuarioDB`, `CarrinhoDB`, `ItemPedidoDB`, `PedidoDB` (inalterados, só sem as classes Pydantic)

- [ ] **Step 1: Substituir `app/models.py` inteiro**

Remove todas as classes Pydantic (`Produto`, `ProdutoCreate`, `Usuario`, `UsuarioCreate`, `ItemCarrinho`, `ItemCarrinhoCreate`, `ItemPedido`, `ItemPedidoCreate`, `Pedido`, `PedidoCreate` — já duplicadas/movidas nos módulos ou nunca usadas, no caso de `ItemCarrinho`/`ItemCarrinhoCreate`), e limpa os imports duplicados:

```python
import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, LargeBinary, Numeric, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from app.database import Base


class ProdutoDB(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    imagem = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    avaliacao = Column(Float, nullable=False)
    ingredientes = Column(JSON, nullable=False)
    categoria = Column(String, nullable=False)


class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    nome = Column(String, nullable=False)
    sobrenome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telefone = Column(String, nullable=True)
    endereco = Column(String, nullable=True)
    ponto_referencia = Column(String, nullable=True)
    numero = Column(Integer)
    password = Column(String, nullable=False)
    foto_url = Column(String, nullable=True)
    foto = Column(LargeBinary, nullable=True)


class CarrinhoDB(Base):
    __tablename__ = "carrinho"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False, default=1)


class ItemPedidoDB(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Integer)
    preco = Column(Float)
    produto = relationship("ProdutoDB")
    pedido = relationship("PedidoDB", back_populates="itens")


class PedidoDB(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    data = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="Pedido aceito")
    itens = relationship("ItemPedidoDB", back_populates="pedido")
    previsao_entrega = Column(DateTime)
    rua_entrega = Column(String)
    numero_entrega = Column(String)
    ponto_referencia = Column(String)
```

- [ ] **Step 2: Confirmar que nada mais importa as classes Pydantic removidas**

```bash
grep -rn "models\.\(Produto\|ProdutoCreate\|Usuario\|UsuarioCreate\|ItemCarrinho\|ItemPedido\b\|Pedido\b\)" app popular_db.py test_db.py
```

Esperado: nenhum resultado (só `models.ProdutoDB`, `models.UsuarioDB` etc., que continuam existindo).

- [ ] **Step 3: Smoke test completo — todos os endpoints**

```bash
docker compose up -d db
uvicorn app.main:app --port 8000 &
sleep 2
curl -s http://localhost:8000/produtos
curl -s -X POST http://localhost:8000/login -H "Content-Type: application/json" -d '{"login":"x","password":"y"}'
curl -s http://localhost:8000/usuarios/1
curl -s http://localhost:8000/pedidos
curl -s http://localhost:8000/pedidos/usuario/1
kill %1
```

Esperado: todas as respostas iguais ao comportamento de antes da refatoração (mesmos formatos, mesmos códigos de erro pra dados inexistentes).

- [ ] **Step 4: Commit**

```bash
git add app/models.py
git commit -m "refactor: reduz models.py so as tabelas SQLAlchemy"
```

---

### Task 7: Atualizar `readme.md` com a nova estrutura

**Files:**
- Modify: `readme.md`

**Interfaces:** nenhuma (documentação)

- [ ] **Step 1: Atualizar a seção "Estrutura do Projeto" do `readme.md`**

Trocar o bloco atual:

```
smash-burger-api/
├── app/
│   ├── main.py            # Aplicação FastAPI e todos os endpoints
│   ├── database.py        # Conexão com PostgreSQL (SQLAlchemy)
│   ├── models.py          # Modelos SQLAlchemy e schemas Pydantic
│   └── create_tables.py   # Script de criação das tabelas
├── static/
│   ├── images/            # Imagens dos produtos
│   └── index.html
├── docs/                  # Documentação dos endpoints
├── requirements.txt       # Dependências do projeto
├── .env.example           # Template de variáveis de ambiente
├── popular_db.py          # Script para popular o banco com produtos
└── test_db.py             # Teste de conexão com o banco
```

por:

```
smash-burger-api/
├── app/
│   ├── main.py             # Cria o app FastAPI, middlewares e inclui os routers
│   ├── database.py         # Conexão com PostgreSQL (SQLAlchemy)
│   ├── models.py           # Tabelas SQLAlchemy
│   ├── dependencies.py     # get_db() compartilhado
│   ├── utils.py            # Helpers compartilhados (ex: obter_hora_brasil)
│   ├── create_tables.py    # Script de criação das tabelas
│   └── modules/
│       ├── auth/           # POST /login (controller.py, usecase.py, schemas.py)
│       ├── produtos/       # GET /produtos
│       ├── usuarios/       # GET/POST /usuarios/{id}
│       └── pedidos/        # POST/GET /pedidos, itens, status
├── static/
│   ├── images/             # Imagens dos produtos
│   └── index.html
├── docs/                   # Documentação dos endpoints
├── requirements.txt        # Dependências do projeto
├── .env.example            # Template de variáveis de ambiente
├── popular_db.py           # Script para popular o banco com produtos
└── test_db.py              # Teste de conexão com o banco
```

- [ ] **Step 2: Commit**

```bash
git add readme.md
git commit -m "docs: atualiza estrutura do projeto no readme"
```
