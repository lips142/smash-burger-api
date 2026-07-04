from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.modules.produtos import usecase

router = APIRouter()


@router.get("/produtos")
def listar_produtos(db: Session = Depends(get_db)):
    return usecase.listar_produtos(db)
