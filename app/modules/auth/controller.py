from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.modules.auth import usecase
from app.modules.auth.schemas import LoginData

router = APIRouter()


@router.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    login_value = data.login or data.username
    return usecase.autenticar_usuario(db, login_value, data.password)
