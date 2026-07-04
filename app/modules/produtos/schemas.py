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
