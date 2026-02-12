from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import models, database

router = APIRouter()

# Dependência para obter sessão do banco
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Listar todos os produtos
@router.get("/produtos", response_model=List[models.Produto])
def listar_produtos(db: Session = Depends(get_db)):
    produtos = db.query(models.ProdutoDB).all()
    return produtos

# Adicionar produto
@router.post("/produtos", response_model=models.Produto)
def adicionar_produto(produto: models.ProdutoCreate, db: Session = Depends(get_db)):
    novo_produto = models.ProdutoDB(
        nome=produto.nome,
        preco=produto.preco,
        imagem=produto.imagem,
        descricao=produto.descricao,
        avaliacao=produto.avaliacao,
        ingredientes=produto.ingredientes,
        categoria=produto.categoria,
    )
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto


@router.get("/produtos/{produto_id}", response_model=models.Produto)
def buscar_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(models.ProdutoDB).filter(models.ProdutoDB.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.delete("/produtos/{produto_id}")
def remover_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(models.ProdutoDB).filter(models.ProdutoDB.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()
    return {"mensagem": "Produto removido com sucesso"}
