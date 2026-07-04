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
