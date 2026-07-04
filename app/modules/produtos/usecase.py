from sqlalchemy.orm import Session

from app import models


def listar_produtos(db: Session):
    return db.query(models.ProdutoDB).all()
