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
