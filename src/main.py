from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

from .resources.database import DatabaseManager
import src.models.paciente
import src.models.protocolo
import src.models.poltrona
import src.models.agendamento
import src.models.prescricao
from .routers import paciente, auth, admin, agendamento, protocolo, poltrona, prescricao


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")

    # Leitura da URL do Banco (prioriza Postgres, fallback para SQLite se necessário)
    db_dsn = os.getenv("POSTGRES_DSN")

    if not db_dsn:
        db_dsn = os.getenv("APP_DB_URL")

    if not db_dsn:
        raise ValueError("Nenhuma string de conexão (POSTGRES_DSN ou APP_DB_URL) encontrada no .env")

    db_manager = DatabaseManager(db_dsn)

    app.state.app_db = db_manager
    app.state.aghu_db = db_manager

    print(f"Database connection pool initialized using: {db_dsn.split('@')[-1]}")  # Log seguro (esconde senha)

    yield

    # Shutdown
    print("Shutting down...")
    await db_manager.close_connection()
    print("Database connection closed.")


app = FastAPI(
    title="Sistema de Agendamento Quimioterapia",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(paciente.router)
app.include_router(admin.router)
app.include_router(agendamento.router)
app.include_router(protocolo.router)
app.include_router(poltrona.router)
app.include_router(prescricao.router)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static", "dist")
ASSETS_DIR = os.path.join(STATIC_DIR, "assets")

if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    file_path = os.path.join(STATIC_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    return JSONResponse(
        status_code=404,
        content={"message": "Frontend build not found. Run 'npm run build' in frontend/ directory."}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
