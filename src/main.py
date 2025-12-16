import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from .resources.database import DatabaseManager, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")

    aghu_dsn = os.getenv("AGHU_DB_URL")
    if not aghu_dsn:
        raise ValueError("AGHU_DB_URL not found in environment variables.")

    app.state.aghu_db = DatabaseManager(aghu_dsn)
    print("AGHU (Postgres) connection pool initialized.")

    async with app.state.aghu_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app_dsn = os.getenv("APP_DB_URL")
    if not app_dsn:
        raise ValueError("APP_DB_URL not found in environment variables.")

    app.state.app_db = DatabaseManager(app_dsn)
    print("Application DB (Postgres) connection pool initialized.")

    async with app.state.app_db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    print("Shutting down...")
    if hasattr(app.state, 'aghu_db'):
        await app.state.aghu_db.close_connection()
    if hasattr(app.state, 'app_db'):
        await app.state.app_db.close_connection()


app = FastAPI(title="Esqueleto de Aplicação Web Full-Stack",
    description="Aplicação Backend monolítica (API REST) em Python/FastAPI, com foco em acesso e agregação de dados heterogêneos.",
    version="1.0.0", lifespan=lifespan, )

origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000", "http://127.0.0.1:8000", ]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"],
    allow_headers=["*"], )

# Serve o frontend Vue 3 empacotado
# app.mount("/assets", StaticFiles(directory="src/static/dist/assets"), name="assets")
#
# @app.get("/")
# async def serve_frontend():
#     """
#     Serve o arquivo index.html do frontend Vue.
#     """
#     return FileResponse(os.path.join("src", "static", "dist", "index.html"))

from .routers import paciente, auth, admin, protocolo, agendamento, prescricao, configuracao

app.include_router(paciente.router)
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(protocolo.router)
app.include_router(agendamento.router)
app.include_router(prescricao.router)
app.include_router(configuracao.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
