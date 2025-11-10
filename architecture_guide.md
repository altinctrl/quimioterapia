# Guia para Geração de Diagrama de Arquitetura

Este documento descreve os componentes e o fluxo de dados da aplicação para que um diagrama de arquitetura possa ser gerado (por exemplo, usando Mermaid.js).

## Componentes Principais

O diagrama deve incluir os seguintes componentes principais:

1.  **Usuário (User):** O ator que interage com a aplicação.
## Arquitetura do Frontend (Vue.js SPA)

O frontend é uma Single-Page Application (SPA) construída com Vue.js 3, Vite e TypeScript. Ele é responsável por toda a interface do usuário e interação com o cliente. A arquitetura é modular e reativa, organizada da seguinte forma:

### 1. Estrutura de Diretórios

*   `src/`: Contém todo o código-fonte do frontend.
*   `src/assets/`: Arquivos estáticos como imagens e CSS global.
*   `src/components/`: Componentes de UI reutilizáveis (e.g., `Button.vue`, `Card.vue`, `DataTable.vue`).
*   `src/layouts/`: Componentes de layout da página (e.g., `DefaultLayout.vue` com sidebar, `LoginLayout.vue` para a página de login).
*   `src/router/`: Configuração do `vue-router`, incluindo a definição de rotas e guardas de navegação.
*   `src/services/`: Serviços, como o `api.ts` que encapsula a comunicação com o backend via Axios.
*   `src/stores/`: Módulos de gerenciamento de estado do Pinia (e.g., `auth.ts`, `ui.ts`).
*   `src/views/`: Componentes de página, que representam as diferentes páginas da aplicação (e.g., `Home.vue`, `Login.vue`, `Pacientes.vue`).

### 2. Fluxo de Navegação e Autenticação

1.  **Inicialização:** Quando o usuário acessa a aplicação, o `main.ts` inicializa o Vue e o `App.vue` é montado.
2.  **Layout Dinâmico:** O `App.vue` usa um `computed` para decidir qual layout (`DefaultLayout` ou `LoginLayout`) deve ser renderizado com base nos metadados da rota atual.
3.  **Autenticação Inicial:** No `onMounted`, o `App.vue` chama a action `initializeAuth` da `authStore`. Essa action tenta validar um token JWT existente no `localStorage` ou obter um novo token usando o `refresh_token` (HttpOnly cookie).
4.  **Roteamento e Guardas:** O `vue-router` (`src/router/index.ts`) controla a navegação. Um guarda de navegação (`beforeEach`) verifica se a rota requer autenticação (`meta: { requiresAuth: true }`).
    *   Se o usuário não estiver autenticado e a rota for protegida, ele é redirecionado para a página de `/login`.
    *   O acesso a rotas de administrador (e.g., `/admin`) é controlado por um `v-if` no layout, que verifica o `isAdmin` computed property da `authStore`.

### 3. Comunicação com a API

*   **Axios Wrapper (`src/services/api.ts`):** Todas as chamadas para a API do backend são feitas através de uma instância customizada do Axios.
*   **Interceptors:**
    *   **Request Interceptor:** Adiciona o token JWT (`Authorization: Bearer ...`) a cada requisição enviada ao backend.
    *   **Response Interceptor:** Lida com erros de autenticação (e.g., status 401). Se um token expirar, ele tenta usar o `refresh_token` para obter um novo token e, em caso de sucesso, reenvia a requisição original de forma transparente.
    *   **Global Loading Indicator:** Os interceptors também controlam um indicador de carregamento global (via `uiStore`), que é exibido sempre que uma requisição está em andamento.

### 4. Gerenciamento de Estado (Pinia)

*   **`authStore` (`src/stores/auth.ts`):**
    *   `user`: Armazena as informações do usuário autenticado.
    *   `accessToken`: Armazena o token JWT.
    *   `isAuthenticated`: Computed property que indica se o usuário está autenticado.
    *   `isAdmin`: Computed property que verifica se o usuário pertence a um grupo específico do Active Directory.
    *   Actions como `login`, `logout`, `fetchUser`, `initializeAuth` encapsulam a lógica de autenticação.
*   **`uiStore` (`src/stores/ui.ts`):**
    *   `isLoading`: Estado booleano que controla a visibilidade do `LoadingIndicator` global.

### 5. Componentes e UI

*   **Componentes Reutilizáveis:** A aplicação utiliza um conjunto de componentes de UI padronizados (`Button`, `Card`, `DataTable`, `Modal`, etc.) para manter a consistência visual e funcional.
*   **Layouts:** Os layouts (`DefaultLayout`, `LoginLayout`) fornecem a estrutura base para as páginas, como a barra de navegação lateral, o cabeçalho e o rodapé.
*   **Notificações:** O `vue-toastification` é usado para exibir mensagens de feedback (sucesso, erro, informação) para o usuário de forma não intrusiva.
3.  **Backend (FastAPI):** O servidor monolítico que expõe a API REST e serve o frontend. É construído com Python e FastAPI.
4.  **Active Directory (AD):** O serviço de diretório usado para autenticação de usuários.
5.  **Bancos de Dados:**
    *   **PostgreSQL (AGHU):** Banco de dados principal do sistema hospitalar AGHU.
    *   **Oracle (AGHU):** Outro banco de dados do sistema hospitalar AGHU.
    *   **SQLite (Local):** Banco de dados local usado pela aplicação para armazenar dados como refresh tokens.

## Fluxo de Dados e Camadas da Arquitetura

O fluxo de dados principal segue uma arquitetura em camadas bem definida. O diagrama deve representar este fluxo:

1.  O **Usuário** interage com o **Frontend**.
2.  O **Frontend** faz requisições HTTP/HTTPS para o **Backend**.
3.  No **Backend**, a requisição passa pelas seguintes camadas:
    *   **Routers (API Routers):** A camada de entrada da API, que define as rotas (endpoints). Os roteadores dependem da camada de autenticação para proteger as rotas.
    *   **Autenticação (JWT):** Middleware que verifica o token JWT do usuário. Para a autenticação inicial (login), ele se comunica com o **Active Directory**.
    *   **Controllers:** A camada de lógica de negócio. Processa a requisição e chama os providers.
    *   **Providers:** A camada de acesso a dados. Executa as consultas SQL.
    *   **Resources:** Gerencia os pools de conexão com os bancos de dados.
    *   **SQL Templates:** Arquivos `.sql` que contêm o código SQL nativo, que são usados pelos providers.
4.  A camada de **Resources** se conecta aos **Bancos de Dados** (PostgreSQL, Oracle, SQLite) para buscar ou modificar dados.

## Relacionamentos

O diagrama deve mostrar os seguintes relacionamentos:

*   `Usuário` -> `Frontend`
*   `Frontend` -> `Backend`
*   `Backend` -> `Routers`
*   `Routers` -> `Controllers`
*   `Routers` -> `Autenticação (JWT)`
*   `Autenticação (JWT)` -> `Active Directory`
*   `Controllers` -> `Providers`
*   `Providers` -> `Resources`
*   `Providers` -> `SQL Templates`
*   `Resources` -> `DB PostgreSQL (AGHU)`
*   `Resources` -> `DB Oracle (AGHU)`
*   `Resources` -> `DB SQLite (Local)`

## Estilo (Opcional)

Se possível, use cores ou estilos diferentes para agrupar visualmente os componentes relacionados, como:

*   Um grupo para o **Frontend**.
*   Um grupo para o **Backend**.
*   Um grupo para as **Camadas de Dados** (Bancos de Dados e SQL Templates).
*   Um grupo para a **Autenticação**.
