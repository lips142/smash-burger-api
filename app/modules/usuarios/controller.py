import base64

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.modules.usuarios import usecase

router = APIRouter()


@router.get("/usuarios/{usuario_id}")
def obter_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = usecase.obter_usuario(db, usuario_id)
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "sobrenome": usuario.sobrenome,
        "endereco": usuario.endereco,
        "ponto_referencia": usuario.ponto_referencia,
        "foto_bytes": base64.b64encode(usuario.foto).decode('utf-8') if usuario.foto else None,
        "email": usuario.email,
        "telefone": usuario.telefone,
    }


@router.post("/usuarios/{usuario_id}")
async def atualizar_usuario(
    usuario_id: int,
    nome: str = Form(...),
    sobrenome: str = Form(""),
    endereco: str = Form(""),
    ponto_referencia: str = Form(""),
    telefone: str = Form(""),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    foto_bytes = await file.read() if file else None
    usecase.atualizar_usuario(db, usuario_id, nome, sobrenome, endereco, ponto_referencia, telefone, foto_bytes)
    return {"success": True, "message": "Perfil atualizado com sucesso"}
