# Banco de Dados e Migrações

## Arquitetura de Dados

O sistema interage com duas fontes de dados distintas (ambas PostgreSQL em desenvolvimento):

### 1. `db_quimio` (Aplicação)
-   **Responsabilidade:** Armazena dados gerados pela nossa aplicação e replica prontuários sob demanda.
-   **Gerenciamento:** Totalmente gerenciado por nós via **Alembic**.
-   **Tabelas Principais:** `pacientes`, `prescricoes`, `protocolos`, `agendamentos`.

### 2. `db_aghu` (Legado / Réplica)
-   **Responsabilidade:** Simula o banco de dados do hospital (AGHU).
-   **Gerenciamento:** Não aplicamos migrações aqui. Em produção, é um banco externo apenas leitura. Em dev, é um Postgres populado via scripts (`src/scripts/seed.py`).
-   **Dados:** Prontuários de pacientes.

---

## Resetando o Ambiente de Dados (Desenvolvimento)

Se o banco de dados local estiver inconsistente ou seja necessário começar "do zero":

1. **Pare os containers e apague os volumes:**
    Isso apaga fisicamente os dados do container.
    ```bash
    podman-compose down -v
    ```

2. **Inicie novamente:**
    ```bash
    podman-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
    ```

3. **Execute os scripts de seed:**
    ```bash
    # Primeiro popular o AGHU (Executar apenas uma vez ou se resetar volumes)
    python src/scripts/seed_aghu.py

    # Depois popular o banco da aplicação (Desenvolvimento diário)
    python src/scripts/seed_dev.py
    ```
