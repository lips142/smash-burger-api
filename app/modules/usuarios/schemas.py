from typing import Optional

from pydantic import BaseModel


class Usuario(BaseModel):
    id: int
    username: str
    nome: str
    sobrenome: str
    email: str
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    ponto_referencia: Optional[str] = None

    class Config:
        from_attributes = True


class UsuarioCreate(BaseModel):
    username: str
    email: str
    password: str
