from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.modules.auth.controller import router as auth_router
from app.modules.produtos.controller import router as produtos_router
from app.modules.usuarios.controller import router as usuarios_router
from app.modules.pedidos.controller import router as pedidos_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router)
app.include_router(produtos_router)
app.include_router(usuarios_router)
app.include_router(pedidos_router)
