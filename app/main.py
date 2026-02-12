from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from typing import Dict, List, Optional
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para garantir que o pedido seja salvo no horário de Brasília
def obter_hora_brasil():
    return datetime.utcnow() - timedelta(hours=3)

class LoginData(BaseModel):
    login: str | None = None
    username: str | None = None
    password: str

class UsuarioCreate(BaseModel): 
    username: str
    nome: str
    sobrenome: str
    numero : int
    email: str
    telefone: int
    endereco: str
    ponto_referencia: Optional[str] = None
    password: str

class ItemPedidoCreate(BaseModel):
    produto_id: int
    quantidade: int
    preco: float

class PedidoCreate(BaseModel):
    usuario_id: int
    total: float
    status: str = "Novo pedido"
    itens: List[ItemPedidoCreate] = []


@app.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    login_value = data.login or data.username
    user = db.query(models.UsuarioDB).filter(
        (models.UsuarioDB.username == login_value) |
        (models.UsuarioDB.email == login_value)
    ).first()

    if user and user.password == data.password:
        return {
            "success": True, 
            "message": "Login realizado com sucesso", 
            "usuario_id": user.id
        }
    raise HTTPException(status_code=401, detail="Login ou senha inválidos")

@app.post("/cadastro")
def cadastro(user: UsuarioCreate, db: Session = Depends(get_db)):
    existente = db.query(models.UsuarioDB).filter(
        (models.UsuarioDB.username == user.username) | (models.UsuarioDB.email == user.email)
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Usuário ou Email já cadastrado")

    novo_usuario = models.UsuarioDB(
        username=user.username, nome=user.nome, sobrenome=user.sobrenome,
        email=user.email, telefone=user.telefone, endereco=user.endereco,
        numero=user.numero, ponto_referencia=user.ponto_referencia, password=user.password
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {"success": True, "usuario_id": novo_usuario.id}


@app.get("/usuarios/{usuario_id}")
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    user = db.query(models.UsuarioDB).filter(models.UsuarioDB.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    num_str = str(user.numero) if user.numero and user.numero != 0 else "S/N"

    return {
        "id": user.id,
        "nome_exibicao": f"{user.nome} {user.sobrenome}",
        "primeiro_nome": user.nome,
        "nome": user.nome,
        "sobrenome": user.sobrenome,
        "email": user.email,
        "endereco": user.endereco,
        "rua": user.endereco, 
        "numero": num_str,
        "ponto_referencia": user.ponto_referencia,
        "telefone": user.telefone,
        "foto_url": user.foto_url
    }



@app.get("/produtos")
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(models.ProdutoDB).all()



@app.post("/pedidos")
def criar_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
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
            numero_entrega=str(user.numero),
            ponto_referencia=user.ponto_referencia
        )
        db.add(novo_pedido)
        db.commit()
        db.refresh(novo_pedido)

        for item in pedido.itens:
            novo_item = models.ItemPedidoDB(
                pedido_id=novo_pedido.id,
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                preco=item.preco
            )
            db.add(novo_item)
        
        db.commit()
        return {"success": True, "message": "Pedido criado", "id": novo_pedido.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/pedidos")
def listar_todos_pedidos(db: Session = Depends(get_db)):
    pedidos = db.query(models.PedidoDB).order_by(models.PedidoDB.data.desc()).all()
    resultado = []
    
    for p in pedidos:
        usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.id == p.usuario_id).first()
        nome_completo = f"{usuario.nome} {usuario.sobrenome}" if usuario else "Cliente"

        resultado.append({
            "id": p.id,
            "usuario_nome": nome_completo,
            "total": float(p.total),
            "status": p.status,
            "data": p.data.isoformat() if p.data else None,
            "rua": p.rua_entrega if p.rua_entrega else (usuario.endereco if usuario else "Não informado"),
            "numero": p.numero_entrega or (str(usuario.numero) if usuario else "S/N"),
            "ponto_referencia": p.ponto_referencia or (usuario.ponto_referencia if usuario else "")
        })
    return resultado

@app.get("/pedidos/usuario/{usuario_id}")
def listar_pedidos_usuario(usuario_id: int, db: Session = Depends(get_db)):
  
    pedidos = db.query(models.PedidoDB).filter(models.PedidoDB.usuario_id == usuario_id).order_by(models.PedidoDB.data.desc()).all()
    
    resultado = []
    for p in pedidos:
    
        data_ajustada = p.data - timedelta(hours=3) if p.data else None
        
        resultado.append({
            "id": p.id, 
            "total": float(p.total), 
            "status": p.status, 
            "data": data_ajustada.isoformat() if data_ajustada else None,
            "rua": p.rua_entrega or "Endereço não informado",
            "numero": p.numero_entrega or "S/N"
        })
    return resultado

@app.get("/pedidos/{pedido_id}/itens")
def listar_itens_pedido(pedido_id: int, db: Session = Depends(get_db)):
    itens = (
        db.query(models.ItemPedidoDB, models.ProdutoDB.nome, models.ProdutoDB.imagem)
        .join(models.ProdutoDB, models.ItemPedidoDB.produto_id == models.ProdutoDB.id)
        .filter(models.ItemPedidoDB.pedido_id == pedido_id).all()
    )
    return [{
        "id": it.id, "nome": n, "imagem": img, 
        "quantidade": it.quantidade, "preco": float(it.preco)
    } for it, n, img in itens]

@app.put("/pedidos/{pedido_id}/status")
def atualizar_status(pedido_id: int, status: str, db: Session = Depends(get_db)):
    pedido = db.query(models.PedidoDB).filter(models.PedidoDB.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    pedido.status = status
    db.commit()
    return {"success": True}