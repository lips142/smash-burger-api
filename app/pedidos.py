from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, database
import datetime

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/pedidos", response_model=models.Pedido)
def criar_pedido(pedido: models.PedidoCreate, db: Session = Depends(get_db)):
    novo_pedido = models.PedidoDB(
        usuario_id=pedido.usuario_id,
        total=pedido.total,
        data=datetime.datetime.utcnow(),
        status=pedido.status  # ← agora respeita o que veio do Flutter
    )
    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)
    return novo_pedido


@router.get("/pedidos/{usuario_id}", response_model=List[models.Pedido])
def listar_pedidos(usuario_id: int, db: Session = Depends(get_db)):
    pedidos = db.query(models.PedidoDB).filter(models.PedidoDB.usuario_id == usuario_id).all()
    if not pedidos:
        raise HTTPException(status_code=404, detail="Nenhum pedido encontrado")
    return pedidos
