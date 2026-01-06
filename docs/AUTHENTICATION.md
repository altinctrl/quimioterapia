# Sistema de Autenticação e Segurança

O framework implementa um sistema de autenticação baseado em **JWT**, projetado para garantir agilidade no desenvolvimento e segurança na persistência da sessão.

## Estratégia de Autenticação

Atualmente, o sistema opera exclusivamente com um provedor simulado. Isso elimina a dependência de serviços externos e redes corporativas nesta fase do projeto.

### Mock Provider

Um provedor estático para validação de acesso local.

* **Comportamento:** Valida as credenciais contra uma base local simulada.
* **Credenciais Padrão:**
  * **Usuário:** `admin`
  * **Senha:** `admin`

---

## Fluxo de Tokens (JWT + Cookies)

A segurança da sessão é baseada em um padrão de **Tokens Duplos**, que separa a identificação do usuário da renovação do acesso.

### 1. Access Token

* **Função:** Identificação imediata do usuário (contém ID, Nome e Permissões).
* **Armazenamento:** Memória do Frontend (State Management/Pinia).
* **Validade:** Curta (ex: 60 minutos).
* **Uso:** Enviado no Header `Authorization: Bearer <token>` em todas as requisições API.

### 2. Refresh Token

* **Função:** Chave de segurança para renovar o acesso sem exigir novo login manual.
* **Armazenamento:** **Cookie HttpOnly**. Por ser invisível ao JavaScript, este método protege o token contra ataques de roubo de dados via scripts maliciosos (XSS).
* **Validade:** Longa (ex: 7 dias).
* **Uso:** Utilizado exclusivamente pela rota `/auth/refresh` quando o Access Token expira.

---

## Ciclo de Vida da Sessão

1. **Login:** O usuário envia as credenciais → O Backend valida via Mock → Retorna o **Access Token** (JSON) e configura o **Refresh Token** (Cookie seguro).
2. **Requisições:** O Frontend anexa o Access Token em cada chamada à API.
3. **Renovação Automática:** Caso o Access Token expire (Erro 401), o Interceptor do Frontend solicita uma renovação. O Backend lê o Cookie de Refresh e, se válido, emite um novo Access Token.
4. **Encerramento:** Ao clicar em "Sair", o sistema limpa o estado do Frontend e solicita ao Backend a invalidação do Cookie de Refresh.
