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
        status=pedido.status 
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

    
@router.put("/pedidos/{pedido_id}/status")
def atualizar_status(pedido_id: int, status: str, db: Session = Depends(get_db)):

    pedido = db.query(models.PedidoDB).filter(models.PedidoDB.id == pedido_id).first()
    
  
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    

    pedido.status = status
    db.commit()
    db.refresh(pedido)
    
    return {"message": "Status atualizado com sucesso", "novo_status": pedido.status}