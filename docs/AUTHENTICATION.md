# Sistema de Autenticação e Integração LDAP

O sistema utiliza uma abordagem híbrida de autenticação e autorização. A validação de credenciais é delegada a um
servidor **LDAP/Active Directory** corporativo, enquanto o gerenciamento de sessão é feito via **JWT (JSON Web Tokens)**.

Os dados do usuário (nome, e-mail e função) são sincronizados do LDAP para o banco de dados local da aplicação no
momento do login, garantindo que o histórico de ações (agendamentos, prescrições) esteja vinculado a um registro
persistente.

---

## 1. Variáveis de Ambiente e Configuração

Para que a autenticação funcione em produção, o arquivo `.env` (ou as variáveis de ambiente do container) deve ser
configurado corretamente.

### Conexão LDAP / Active Directory

Estas variáveis definem como a aplicação se conecta ao diretório corporativo do hospital.

| Variável            | Descrição                                                                                         | Exemplo Dev                   | Exemplo Prod                            |
|---------------------|---------------------------------------------------------------------------------------------------|-------------------------------|-----------------------------------------|
| `AD_SERVER`         | Endereço do servidor LDAP (protocolo://host:porta).                                               | `ldap://localhost:3389`       | `ldap://ad.hc.gov.br:389`               |
| `AD_DOMAIN`         | Domínio da rede.                                                                                  | `hc.gov.br`                   | `hc.gov.br`                             |
| `AD_BASEDN`         | Base DN para busca de usuários e grupos.                                                          | `dc=hc,dc=gov,dc=br`          | `DC=hc,DC=gov,DC=br`                    |
| `AD_ADMIN_DN`       | **Service Account**: Usuário com permissão de leitura no AD para buscar grupos do usuário logado. | `cn=admin,dc=hc,dc=gov,dc=br` | `CN=ServiceAccount,OU=Service,DC=hc...` |
| `AD_ADMIN_PASSWORD` | Senha do Service Account.                                                                         | `admin`                       | `S3nh4Segura!`                          |

### Segurança e JWT

Configurações para geração e validação dos tokens de sessão.

| Variável                     | Descrição                                                                                           | Padrão |
|------------------------------|-----------------------------------------------------------------------------------------------------|--------|
| `JWT_SECRET`                 | Chave privada para assinatura do token. **Em produção, use uma string aleatória longa e complexa.** | -      |
| `JWT_EXP_MINUTES`            | Tempo de vida do **Access Token**.                                                                  | `60`   |
| `JWT_REFRESH_TOKEN_EXP_DAYS` | Tempo de vida do **Refresh Token**.                                                                 | `7`    |

### Mapeamento de Funções

| Variável         | Descrição                                                                 |
|------------------|---------------------------------------------------------------------------|
| `ROLES_MAP_PATH` | Caminho absoluto ou relativo para o arquivo JSON de mapeamento de grupos. |

---

## 2. Mapeamento de Grupos (RBAC)

A aplicação não utiliza os nomes de grupos do AD diretamente. Em vez disso, ela traduz os grupos do LDAP para **Roles**
internos do sistema através do arquivo `roles_map.json`.

**Arquivo:** `src/roles_map.json`

Este arquivo deve ser editado pela equipe de implantação para corresponder à estrutura de grupos do Hospital.

**Estrutura:**

```json
{
  "NOME_DO_GRUPO_NO_LDAP": "ROLE_INTERNA",
  "OUTRO_GRUPO_LDAP": "ROLE_INTERNA",
  "default": "ROLE_PADRAO"
}
```

* **Chave:** O `cn` (Common Name) do grupo no Active Directory.
* **Valor:** A role interna que o sistema reconhece (`admin`, `medico`, `farmacia` ou `enfermeiro`).
* **Prioridade:** Se um usuário pertencer a múltiplos grupos, o sistema priorizará a role `admin`. Caso contrário, usará
  a primeira correspondência encontrada.

**Exemplo Prático:**
Se no AD do hospital os médicos estão no grupo `G_MEDICOS_ONCOLOGIA`, o JSON deve ficar assim:

```json
{
  "G_MEDICOS_ONCOLOGIA": "medico",
  "G_TI_SUPORTE": "admin"
}
```

---

## 3. Fluxo de Autenticação

1. **Credenciais:** O usuário envia `username` e `password` para a API (`/api/login`).
2. **Bind de Usuário:** O backend tenta fazer um "Bind" no servidor LDAP usando as credenciais fornecidas. Se falhar, retorna erro 401.
3. **Busca de Grupos (Service Account):**
    * Como usuários comuns muitas vezes não têm permissão para ler atributos de outros objetos, o backend desconecta o usuário e conecta com o `AD_ADMIN_DN` (Service Account).
    * O sistema busca todos os grupos (`objectClass=groupOfNames` ou equivalente) onde o usuário é membro (`member=CN=usuario...`).
4. **Resolução de Role:** O backend cruza a lista de grupos retornada pelo LDAP com o arquivo `roles_map.json` para determinar a permissão do usuário.
5. **Sincronização Local (Get-or-Create):**
    * O sistema verifica se o usuário já existe na tabela `users` do Postgres.
    * **Se existir:** Atualiza e-mail, display name e roles com os dados frescos do LDAP.
    * **Se não existir:** Cria um novo registro na tabela `users`.
6. **Emissão de Tokens:**
   * Gera um **Access Token** (JWT) contendo o `sub` (username) e claims.
   * Gera um **Refresh Token** opaco, salvo no banco e enviado via Cookie HttpOnly.

---

## 4. Ambiente de Desenvolvimento

Para desenvolvimento local, utilizamos um container OpenLDAP (`osixia/openldap`) pré-populado via arquivo `users.ldif`.

* **Painel Admin LDAP:** Acessível em `http://localhost:8081` (phpLDAPadmin).
* **Usuários de Teste (Senha: `123`):**
  * `admin.sistema` (Grupo: Administradores -> Role: admin)
  * `dr.joao` (Grupo: Medicos -> Role: medico)
  * `ana.farmacia` (Grupo: Farmacia -> Role: farmacia)
  * `ana.enfermagem` (Grupo: Enfermagem -> Role: enfermeiro - *default*)

---

## 5. Limitações e Segurança

### Controle de Acesso no Backend

Embora o Frontend utilize a informação de `role` para ocultar menus e telas, a validação de autorização (RBAC) nos
endpoints da API **não está completa**.

* **Status Atual:** O decorador `require_groups` existe e pode proteger rotas, verificando se o usuário possui os grupos
  necessários no token.
* **Risco:** Se uma rota não estiver explicitamente protegida com `require_groups`, um usuário autenticado poderá 
  acessá-la via chamadas diretas à API, embora não consiga vê-la na interface. Isso pode ser um problema agora, caso 
  outros usuários do hospital possam se autenticar nessa aplicação, ou no futuro caso não se permita mais que usuários
  não médicos criem prescrições.
* **Recomendação:** Ao implantar, certifique-se de que endpoints críticos de escrita/deleção estejam protegidos pelo
  `require_groups` no `auth_handler.py`.

### Service Account do LDAP

O sistema requer uma conta de serviço (`AD_ADMIN_DN`) para buscar grupos. Recomenda-se criar um usuário de serviço no AD
com permissões estritas de **Leitura (Read-Only)** na OU onde residem os usuários e grupos da aplicação, minimizando
riscos de segurança.

---

## 6. Arquivos e Estrutura do Módulo de Autenticação

Abaixo estão listados os principais arquivos envolvidos no fluxo de autenticação, sua localização no projeto e suas 
respectivas responsabilidades.

### Configuração e Serviços

| Arquivo          | Caminho Sugerido               | Responsabilidade                                                                                                                                                                   |
|------------------|--------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **LDAP Service** | `src/services/ldap_service.py` | Responsável pela conexão direta com o servidor LDAP/AD. Executa o *bind* das credenciais do usuário e realiza a busca de grupos utilizando a conta de serviço (*Service Account*). |
| **Roles Map**    | `src/roles_map.json`           | Arquivo JSON editável que define a equivalência entre os grupos do Active Directory ("MemberOf") e as *Roles* internas da aplicação (ex: `G_TI_SUPORTE` = `admin`).                |
| **Auth Handler** | `src/auth/auth_handler.py`     | Núcleo de segurança JWT. Contém a lógica para codificar/decodificar tokens, verificar validade e injetar o usuário atual (`get_current_user`) nas rotas protegidas.                |

### Camada de Aplicação (API)

| Arquivo             | Caminho Sugerido                     | Responsabilidade                                                                                                                                                             |
|---------------------|--------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Auth Router**     | `src/routers/auth_router.py`         | Define os *endpoints* HTTP (`/login`, `/refresh`, `/logout`, `/users/me`). É a porta de entrada que recebe as requisições do frontend.                                       |
| **Auth Controller** | `src/controllers/auth_controller.py` | Orquestrador das regras de negócio. Recebe os dados do Router, chama o LDAP para validar, e coordena a criação/atualização do usuário no banco local e a emissão dos tokens. |
| **Auth Schema**     | `src/schemas/auth_schema.py`         | Define os modelos Pydantic (contratos de dados) para entrada e saída da API, garantindo a validação dos tipos de dados (ex: `LoginRequest`, `UserSchema`).                   |

### Persistência de Dados

| Arquivo           | Caminho Sugerido                            | Responsabilidade                                                                                                                                               |
|-------------------|---------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Auth Model**    | `src/models/auth_model.py`                  | Modelos ORM (SQLAlchemy) que representam as tabelas `users` (perfil sincronizado) e `refresh_tokens` (segurança de sessão) no banco de dados.                  |
| **Auth Provider** | `src/providers/auth_sqlalchemy_provider.py` | Camada de abstração de banco de dados. Executa as queries SQL para buscar, criar ou atualizar usuários e tokens, isolando a lógica de banco dos controladores. |

### Infraestrutura (Dev/Deploy)

| Arquivo            | Caminho Sugerido            | Responsabilidade                                                                                                                           |
|--------------------|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| **Users LDIF**     | `ldap_bootstrap/users.ldif` | Arquivo de carga inicial usado apenas em desenvolvimento para popular o container OpenLDAP com usuários e grupos de teste.                 |
| **Docker Compose** | `docker-compose.prod.yml`   | Define os serviços de produção, incluindo as variáveis de ambiente cruciais para a conexão LDAP (`AD_SERVER`, `AD_BASEDN`) e persistência. |
