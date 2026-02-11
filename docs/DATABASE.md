# Banco de Dados e Migrações

## Arquitetura de Dados

O sistema opera com distinção clara entre dados da aplicação e dados legados.

### 1. `db_quimio` (Aplicação)

Armazena dados gerados pela nossa aplicação e replica prontuários sob demanda.

- **Dev:** Container definido em `docker-compose.yml`. Acessado via `localhost:5432`.
- **Prod:** Container (`quimio_db_prod`) definido em `docker-compose.prod.yml`. Acessado internamente via `db_app:5432`.

### 2. `db_aghu` (Legado / Réplica)

Simula o banco de dados do hospital (AGHU).

- **Dev:** Container definido em `docker-compose.dev.yml`. Acessado via `localhost:5433`.
- **Prod:** A aplicação espera conectar-se a um banco existente na rede ou simulado pelo container de dev via rede
  externa. Apenas leitura.

---

## População de Dados

### Em Desenvolvimento (`seed_aghu.py` e `seed_dev.py`)

- **Objetivo:** Gerar massa de dados para testes (pacientes falsos, agendamentos, prescrições).
- **Execução:** Manual, via terminal (`python -m src.scripts.seed_aghu` e `python -m src.scripts.seed_dev`).
- **Comportamento:** Destrutivo. Limpa tabelas antes de inserir.

### Em Produção (`seed_prod.py`)

- **Objetivo:** Garantir que as tabelas existam no banco de dados e que o sistema tenha as configurações mínimas para
  funcionar (Vagas, Horários, Tags, Diluentes).
- **Execução:** Automática (via `entrypoint.sh`) toda vez que o container sobe.
- **Comportamento:** Idempotente. Verifica se a configuração `id=1` existe. Se existir, não faz nada. Se não existir,
  cria os dados iniciais.
