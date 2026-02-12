from app.database import Base, engine
from app import models

def criar_tabelas():
    print("Criando tabelas no banco smashdb...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    criar_tabelas()
