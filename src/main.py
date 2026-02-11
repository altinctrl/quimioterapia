import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.resources.database import app_engine
from src.resources.database_aghu import aghu_engine
from src.routers import auth_router, agendamento_router, configuracao_router, paciente_router, prescricao_router, protocolo_router, equipe_router, relatorio_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicação...")
    yield
    print("Encerrando conexões com o banco de dados...")
    await app_engine.dispose()
    await aghu_engine.dispose()
    print("Conexões encerradas.")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agendamento_router.router)
app.include_router(auth_router.router)
app.include_router(configuracao_router.router)
app.include_router(equipe_router.router)
app.include_router(paciente_router.router)
app.include_router(prescricao_router.router)
app.include_router(protocolo_router.router)
app.include_router(relatorio_router.router)

static_path = "src/static"

if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")

    @app.exception_handler(404)
    async def custom_404_handler(request, __):
        return FileResponse(f"{static_path}/index.html")
else:
    print(f"AVISO: Pasta '{static_path}' não encontrada. O frontend não será servido pelo FastAPI.")
