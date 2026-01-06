# Banco de Dados e Migrações

Este documento explica a arquitetura de dados do projeto e como gerenciar as alterações no esquema do banco de dados utilizando o **Alembic**.

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

## Gerenciando Migrações (Alembic)

As migrações controlam apenas o banco `db_quimio`.

### Comandos Principais

#### Criar uma nova migração
Sempre que um modelo em `src/models/` é alterado, uma nova revisão deve ser gerada:

```bash
alembic revision --autogenerate -m "descricao_da_mudanca"
```

*O arquivo gerado em `alembic/versions/` deve ser verificado para garantir que o script está correto.*

#### Aplicar migrações (Atualizar o banco)

Para aplicar as mudanças pendentes no banco de dados:

```bash
alembic upgrade head
```

#### Reverter migrações

Para desfazer a última migração aplicada:

```bash
alembic downgrade -1
```

Ou para voltar ao estado zero (cuidado, apaga todos os dados):

```bash
alembic downgrade base
```

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
podman-compose up --build
```

3. **Recrie o banco legado:**
```bash
podman-compose exec db psql -U user -d postgres -c "CREATE DATABASE db_aghu;"
```

4. **Execute as migrações e seeds:**
```bash
python src/scripts/seed.py
```
