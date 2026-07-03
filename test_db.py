from sqlalchemy import create_engine

from app.database import DATABASE_URL

engine = create_engine(DATABASE_URL, client_encoding='utf8')


try:
    with engine.connect() as conn:
        print("Conexão com PostgreSQL bem-sucedida!")
except Exception as e:
    print("Erro de conexão:", e)
