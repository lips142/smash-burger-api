from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, database

router = APIRouter()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/carrinho/{usuario_id}", response_model=List[models.ItemCarrinho])
def listar_carrinho(usuario_id: int, db: Session = Depends(get_db)):
    return db.query(models.CarrinhoDB).filter(models.CarrinhoDB.usuario_id == usuario_id).all()

@router.post("/carrinho", response_model=models.ItemCarrinho)
def adicionar_item(item: models.ItemCarrinhoCreate, db: Session = Depends(get_db)):
    novo_item = models.CarrinhoDB(**item.dict())
    db.add(novo_item)
    db.commit()
    db.refresh(novo_item)
    return novo_item

@router.delete("/carrinho/{item_id}")
def remover_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(models.CarrinhoDB).filter(models.CarrinhoDB.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(item)
    db.commit()
    return {"mensagem": "Item removido do carrinho"}
