from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models


def obter_usuario(db: Session, usuario_id: int):
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


def atualizar_usuario(
    db: Session,
    usuario_id: int,
    nome: str,
    sobrenome: str,
    endereco: str,
    ponto_referencia: str,
    telefone: str,
    foto_bytes: Optional[bytes],
):
    usuario = db.query(models.UsuarioDB).filter(models.UsuarioDB.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario.nome = nome
    usuario.sobrenome = sobrenome
    usuario.endereco = endereco
    usuario.ponto_referencia = ponto_referencia
    usuario.telefone = telefone

    if foto_bytes is not None:
        usuario.foto = foto_bytes

    db.commit()
    db.refresh(usuario)
    return usuario
