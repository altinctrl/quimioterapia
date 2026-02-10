# Guia de Configuração e Instalação

Este guia detalha como configurar o ambiente de desenvolvimento. Atualmente, utilizamos uma abordagem híbrida: os bancos de dados rodam em um **container** (para isolamento e facilidade), enquanto o Backend e Frontend rodam **nativamente** na máquina (para performance e debugging).

## Pré-requisitos

- **Python 3.10** ou superior
- **Node.js 18** ou superior
- **Podman Compose** ou **Docker Compose**
- **Git**

---

## 1. Configuração dos Bancos de Dados

O projeto depende de dois bancos de dados PostgreSQL que rodam no mesmo container:
1.  `db_quimio`: Banco de dados principal da aplicação.
2.  `db_aghu`: Banco de dados que simula o sistema legado do hospital (apenas leitura/validação).

### Passo a passo:

1.  **Inicie o container do banco de dados:**
    Na raiz do projeto, execute:
    ```bash
    podman-compose up --build
    ```

2.  **Verifique/Crie o banco legado (`db_aghu`):**
    O container padrão cria apenas o `db_quimio`. Você precisa criar o segundo banco manualmente na primeira vez.

    Execute o comando abaixo para criar o `db_aghu`:
    ```bash
    podman-compose exec db psql -U user -d postgres -c "CREATE DATABASE db_aghu;"
    ```
    *Se retornar um erro dizendo que o banco já existe, pode ignorar.*

3.  **Confira se ambos existem:**
    ```bash
    podman-compose exec db psql -U user -l
    ```
    Você deve ver `db_quimio` e `db_aghu` na lista.

---

## 2. Configuração do Backend (FastAPI)

1.  **Crie o ambiente virtual (na raiz do projeto):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure as variáveis de ambiente:**
    Copie o exemplo e ajuste se necessário (o padrão costuma funcionar para dev local).
    ```bash
    cp .env.example .env
    ```

4.  **Popule os bancos de dados (Seeds):**
    Para ter dados iniciais para trabalhar:
    ```bash
    # Popula o banco de dados com pacientes/prescrições simulados
    python src/scripts/seed_dev.py
    ```

5.  **Inicie o servidor:**
    ```bash
    uvicorn src.main:app --reload
    ```

---

## 3. Configuração do Frontend (Vue.js)

Abra um novo terminal e navegue até a pasta `frontend/`.

1.  **Instale as dependências:**
    ```bash
    cd frontend
    npm install
    ```

2.  **Inicie o servidor de desenvolvimento:**
    ```bash
    npm run dev
    ```

O frontend estará disponível em `http://localhost:5173`.
