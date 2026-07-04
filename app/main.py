from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from typing import List, Optional
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import base64
from app.dependencies import get_db
from app.utils import obter_hora_brasil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")


class LoginData(BaseModel):
    login: Optional[str] = None
    username: Optional[str] = None
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



@app.get("/produtos") 
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(models.ProdutoDB).all()

@app.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    login_value = data.login or data.username
    user = db.query(models.UsuarioDB).filter(
        (models.UsuarioDB.username == login_value) |
        (models.UsuarioDB.email == login_value)
    ).first()

    if user and user.password == data.password:
        return {"success": True, "usuario_id": user.id, "message": "Login realizado com sucesso"}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

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

@app.get("/pedidos")
def listar_todos_pedidos(db: Session = Depends(get_db)):
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

@app.get("/pedidos/{pedido_id}/itens")
def listar_itens_pedido(pedido_id: int, db: Session = Depends(get_db)):
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

@app.get("/pedidos/usuario/{usuario_id}")
def listar_pedidos_usuario(usuario_id: int, db: Session = Depends(get_db)):
    
    print(f"Buscando pedidos para o usuário: {usuario_id}")
    
    pedidos = db.query(models.PedidoDB).filter(models.PedidoDB.usuario_id == usuario_id).all()
    

    if not pedidos:
        return []
        
    return pedidos

@app.get("/usuarios/{usuario_id}")
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
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

@app.post("/usuarios/{usuario_id}")
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
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario.nome = nome
    usuario.sobrenome = sobrenome
    usuario.endereco = endereco
    usuario.ponto_referencia = ponto_referencia
    usuario.telefone = telefone

    if file:
        conteudo = await file.read()
        usuario.foto = conteudo

    db.commit()
    db.refresh(usuario)

    return {"success": True, "message": "Perfil atualizado com sucesso"}

@app.put("/pedidos/{pedido_id}/status")
def atualizar_status_pedido(pedido_id: int, status: str, db: Session = Depends(get_db)):
    pedido = db.query(models.PedidoDB).filter(models.PedidoDB.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    pedido.status = status
    db.commit()
    db.refresh(pedido)
    return {"success": True, "status": pedido.status}