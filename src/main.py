from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.resources.database import app_engine, aghu_engine
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

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agendamento.router)
app.include_router(auth.router)
app.include_router(configuracao.router)
app.include_router(equipe.router)
app.include_router(paciente.router)
app.include_router(prescricao.router)
app.include_router(protocolo.router)
app.include_router(relatorio.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
