from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models


def autenticar_usuario(db: Session, login_value: str, password: str):
    user = db.query(models.UsuarioDB).filter(
        (models.UsuarioDB.username == login_value) |
        (models.UsuarioDB.email == login_value)
    ).first()

    if user and user.password == password:
        return {"success": True, "usuario_id": user.id, "message": "Login realizado com sucesso"}
    raise HTTPException(status_code=401, detail="Credenciais inválidas")
