import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, LargeBinary, Numeric, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship

from app.database import Base


class ProdutoDB(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    imagem = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    avaliacao = Column(Float, nullable=False)
    ingredientes = Column(JSON, nullable=False)
    categoria = Column(String, nullable=False)


class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    nome = Column(String, nullable=False)
    sobrenome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    telefone = Column(String, nullable=True)
    endereco = Column(String, nullable=True)
    ponto_referencia = Column(String, nullable=True)
    numero = Column(Integer)
    password = Column(String, nullable=False)
    foto_url = Column(String, nullable=True)
    foto = Column(LargeBinary, nullable=True)


class CarrinhoDB(Base):
    __tablename__ = "carrinho"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False, default=1)


class ItemPedidoDB(Base):
    __tablename__ = "itens_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"))
    produto_id = Column(Integer, ForeignKey("produtos.id"))
    quantidade = Column(Integer)
    preco = Column(Float)
    produto = relationship("ProdutoDB")
    pedido = relationship("PedidoDB", back_populates="itens")


class PedidoDB(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    data = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="Pedido aceito")
    itens = relationship("ItemPedidoDB", back_populates="pedido")
    previsao_entrega = Column(DateTime)
    rua_entrega = Column(String)
    numero_entrega = Column(String)
    ponto_referencia = Column(String)
