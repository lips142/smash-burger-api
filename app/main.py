from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from typing import Dict, List, Optional
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from fastapi import UploadFile, File, Form
from app import pedidos
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(pedidos.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


import base64

@app.get("/usuarios/{usuario_id}")
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    user = db.query(models.UsuarioDB).filter(models.UsuarioDB.id == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

   
    foto_blob = getattr(user, 'foto', None)
    foto_base64 = None
    if foto_blob:
        import base64
        foto_base64 = base64.b64encode(foto_blob).decode('utf-8')

    return {
        "id": user.id,
        "nome": user.nome,
        "sobrenome": user.sobrenome,
        "email": user.email,
        "endereco": user.endereco,
        "ponto_referencia": user.ponto_referencia,
        "telefone": user.telefone,
        "foto_bytes": foto_base64
    }
@app.post("/usuarios/{usuario_id}")
async def atualizar_usuario(
    usuario_id: int,
    nome: str = Form(...),
    sobrenome: str = Form(...),
    endereco: str = Form(...),
    ponto_referencia: str = Form(""), 
    telefone: str = Form(""),         
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
   
    user = db.query(models.UsuarioDB).filter(models.UsuarioDB.id == usuario_id).first()
    
    if not user:
        print(f"ERRO: Usuário {usuario_id} não encontrado no banco.")
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    try:
       
        user.nome = nome
        user.sobrenome = sobrenome
        user.endereco = endereco
        user.ponto_referencia = ponto_referencia
        user.telefone = telefone
        
        if file:
            user.foto = await file.read() 

    
        db.commit()
        db.refresh(user)
        
        print(f"SUCESSO: Usuário {usuario_id} atualizado para {nome} {sobrenome}")
        return {"status": "sucesso", "nome_atualizado": user.nome}

    except Exception as e:
        db.rollback() 
        print(f"ERRO NO BANCO: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao salvar no banco")

@app.get("/produtos")
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(models.ProdutoDB).all()



@app.post("/pedidos")
def criar_pedido(pedido: PedidoCreate, db: Session = Depends(get_db)):
    # 1. VEJA SE CHEGOU ALGO NO TERMINAL DO PYTHON
    print("========================================")
    print(f"RECEBIDO DO FLUTTER: {pedido.json()}") 
    print(f"QUANTIDADE DE ITENS NA LISTA: {len(pedido.itens)}")
    print("========================================")

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
        db.flush() 

        if not pedido.itens:
            print("AVISO: A lista de itens veio VAZIA do frontend!")

        for item in pedido.itens:
            print(f"Salvando item: Produto {item.produto_id}, Qtd {item.quantidade}")
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
        print(f"ERRO AO SALVAR: {e}")
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
    itens_db = (
        db.query(models.ItemPedidoDB, models.ProdutoDB.nome, models.ProdutoDB.imagem)
        .join(models.ProdutoDB, models.ItemPedidoDB.produto_id == models.ProdutoDB.id)
        .filter(models.ItemPedidoDB.pedido_id == pedido_id).all()
    )

    resultado = []
    for item_pedido, nome_prod, imagem_prod in itens_db:
        resultado.append({
            "id": item_pedido.id,
            "quantidade": item_pedido.quantidade,
            "preco": float(item_pedido.preco), # ADICIONE ISSO para o Painel HTML calcular valores
            "nome": nome_prod,
            "imagem": f"http://10.0.2.2:8000/static/imagens/{imagem_prod}" if imagem_prod else None
        })
    return resultado