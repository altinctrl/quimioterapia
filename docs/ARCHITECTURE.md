# Arquitetura Técnica do Sistema

Este documento detalha a estrutura interna do projeto, os padrões de design utilizados e a organização dos módulos Frontend e Backend. O sistema foi projetado com foco em desacoplamento, testabilidade e separação clara de responsabilidades.

## Visão Geral

A aplicação é uma solução Full-Stack moderna:

-   **Backend:** API RESTful construída com Python e FastAPI.
-   **Frontend:** Single Page Application (SPA) construída com Vue.js 3, Vite e TypeScript.
-   **Banco de Dados:** PostgreSQL.

---

## 1. Arquitetura do Backend

O Backend segue uma arquitetura em camadas estrita. O fluxo de dados é unidirecional e previsível.

**Fluxo da Requisição:**
`Router` → `Controller` → `Provider` → `Database`

### Camadas

#### A. Routers (`src/routers/`)
A porta de entrada da API.
-   **Responsabilidade:** Definir endpoints HTTP (GET, POST, etc.), validar dados de entrada/saída (usando schemas Pydantic) e gerenciar a injeção de dependência.
-   **Regra:** Não contém regras de negócio. Apenas repassa a chamada para o Controller adequado.
-   **Exemplo:** O `agendamento.py` recebe um JSON, valida se os campos estão corretos e chama `controller.criar_agendamento()`.

#### B. Controllers (`src/controllers/`)
O coração da aplicação.
-   **Responsabilidade:** Contém as regras de negócio.
-   **Regra:** É agnóstico ao banco de dados. Ele não executa SQL. Ele solicita dados através de interfaces abstratas (Providers).
-   **Exemplo:** O `agendamento_controller.py` verifica: *"Há vagas suficientes para este protocolo?"*. Se tudo estiver ok, ele pede ao Provider para salvar.

#### C. Providers (`src/providers/`)
A camada de acesso a dados.
-   **Responsabilidade:** Comunicar-se com o mundo externo (Banco de Dados ou APIs).
-   **Implementação:** Utilizamos o padrão **Repository/Provider**.
    -   **Interfaces (`interfaces/`):** Contratos que definem *o que* pode ser feito (ex: `buscar_paciente`).
    -   **Implementações (`implementations/`):** O código real que usa SQLAlchemy para falar com o Postgres.
-   **Benefício:** Permite testar os Controllers usando "Mock Providers" sem precisar de um banco de dados real.

### Mapeamento dos Módulos

A aplicação é modularizada por domínios de negócio. Abaixo, a relação entre os arquivos técnicos e os módulos funcionais:

| Módulo         | Rota Base       | Controller Principal         | Tabelas Principais           | Fonte de Dados          |
|:---------------|:----------------|:-----------------------------|:-----------------------------|:------------------------|
| **Agenda**     | `/agendamento`  | `agendamento_controller.py`  | `agendamentos`               | Local (Postgres)        |
| **Prescrição** | `/prescricao`   | `prescricao_controller.py`   | `prescricoes`                | Local (Postgres)        |
| **Pacientes**  | `/paciente`     | `paciente_controller.py`     | `pacientes`, `aip_pacientes` | Local (Postgres) e AGHU |
| **Protocolos** | `/protocolo`    | `protocolo_controller.py`    | `protocolos`                 | Local (Postgres)        |
| **Ajustes**    | `/configuracao` | `configuracao_controller.py` | `configuracoes`              | Local (Postgres)        |

---

## 2. Arquitetura do Frontend

O frontend é uma SPA reativa construída com Vue 3, Pinia para gerenciamento de estado e TailwindCSS para estilização.

### Estrutura de Diretórios

-   `src/views/`: As páginas da aplicação (ex: `ViewAgenda.vue`, `ViewLogin.vue`).
-   `src/components/`: Componentes reutilizáveis (botões, cards, modais, tabelas).
-   `src/stores/`: Gerenciamento de estado global (Pinia).
-   `src/services/`: Comunicação com a API (Axios).

### Gerenciamento de Estado

Pinia é utilizado para compartilhar dados entre componentes e evitar "prop drilling".

-   **`storeAuth.ts`:** Armazena o usuário logado, permissões e controla o token JWT.
-   **`storeAgendamento.ts`, `storePaciente.ts`, etc.:** Stores específicas de domínio que armazenam as listas de dados buscados da API.

### Camada de Serviço e Axios

Toda a comunicação HTTP reside em `src/services/api.ts`.

-   **Interceptors:** Configurações globais do Axios.
    1.  **Request:** Adiciona automaticamente o header `Authorization: Bearer <token>` em todas as chamadas.
    2.  **Response:** Monitora erros `401 Unauthorized`. Se o token expirar, o interceptor tenta usar o **Refresh Token** (cookie) para renovar a sessão transparentemente, sem deslogar o usuário.

---

## 3. Banco de Dados

Dois bancos de dados são usados para separar responsabilidades:

1.  **`db_quimio` (Aplicação):** Onde gravamos nossos dados (agendamentos, configurações). Gerenciado via **Alembic**.
2.  **`db_aghu` (Legado):** Uma réplica (ou mock) apenas leitura dos dados hospitalares. Não sofre migrações por nossa aplicação.

Para mais detalhes sobre banco de dados, consulte [DATABASE_MIGRATIONS.md](DATABASE.md).
