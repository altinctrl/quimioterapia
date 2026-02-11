# Guia de Configuração e Instalação

Este guia detalha como configurar o ambiente de desenvolvimento. Atualmente, utilizamos uma abordagem híbrida: os bancos de dados rodam em um **container** (para isolamento e facilidade), enquanto o Backend e Frontend rodam **nativamente** na máquina (para performance e debugging).

## Pré-requisitos

- **Python 3.10** ou superior
- **Node.js 18** ou superior
- **Podman Compose** ou **Docker Compose**
- **Git**

---

## 1. Configuração dos Containers

O projeto depende de dois bancos de dados PostgreSQL e dos serviços LDAP:
1.  `db_quimio`: Banco de dados principal da aplicação.
2.  `db_aghu`: Banco de dados que simula o sistema legado do hospital (apenas leitura/validação).
3.  `openldap_server`: Servidor LDAP para autenticação.
4.  `phpldapadmin`: Interface web para o servidor LDAP.

### Alternativas:

1.  **Inicie todos os serviços no ambiente de desenvolvimento:**
    Na raiz do projeto, execute:
    ```bash
    podman-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
    ```

2.  **Inicie apenas o banco de dados principal em produção:**
    Na raiz do projeto, execute:
    ```bash
    podman-compose up --build
    ```

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
    # Primeiro popular o AGHU (Executar apenas uma vez ou se resetar volumes)
    python src/scripts/seed_aghu.py

    # Depois popular o banco da aplicação (Desenvolvimento diário)
    python src/scripts/seed_dev.py
    ```
    Ou apenas crie as tabelas e carregue as configurações padrão se estiver em produção:
    ```bash
    python src/scripts/seed_prod.py
    ```

5.  **Inicie o servidor:**
    ```bash
    uvicorn src.main:app --reload # Remova a flag --reload se estiver em produção
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
