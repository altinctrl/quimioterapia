# Guia de Configuração e Instalação

Este projeto suporta dois fluxos de trabalho distintos:

1. **Desenvolvimento:** Bancos de dados e servidor LDAP em containers; Backend e Frontend rodam nativamente na máquina
   com hot-reload habilitado.
2. **Produção:** Backend e Frontend rodam juntos em uma imagem Docker otimizada, conectando-se aos serviços externos
   via rede Docker. Deve ser configurado se serviços de suporte forem executados em um ambiente separado.

---

### Pré-requisitos

- **Python 3.14** ou superior
- **Node.js 22.12** ou superior
- **Podman Compose** ou **Docker Compose**
- **Git**

---

## 1. Ambiente de Desenvolvimento

Use este modo para codificar. As alterações no código refletem imediatamente.

### Passo 1: Infraestrutura

Inicie os serviços de suporte (Banco de dados da aplicação, AGHU, servidor LDAP e WebUI LDAP).
Na raiz do projeto, execute:

```bash
podman-compose -f docker-compose.yml -f docker-compose.dev.yml -p quimio_dev up --build
```

**Isso criará a rede `quimioterapia_quimio_network`.**

### Passo 2: Backend

1. **Crie o ambiente virtual na raiz do projeto:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente:**
   Copie o exemplo e ajuste se necessário (o padrão costuma funcionar para dev local).
   ```bash
   cp .env.example .env
   ```

4. **Popule os bancos de dados:**
   Para ter dados iniciais para trabalhar:
   ```bash
   # Primeiro popular o AGHU (Executar apenas uma vez ou se resetar volumes)
   python src/scripts/seed_aghu.py

   # Depois popular o banco da aplicação (Desenvolvimento diário)
   python src/scripts/seed_dev.py
   ```

5. **Inicie o servidor:**
   ```bash
   uvicorn src.main:app --reload
   ```

**A API ficará disponível em: `http://localhost:8000`**

### Passo 3: Frontend

Abra um novo terminal e navegue até a pasta `frontend/`.

1. **Instale as dependências:**
   ```bash
   cd frontend
   npm install
   ```

2. **Inicie o servidor de desenvolvimento:**
   ```bash
   npm run dev
   ```

**O frontend estará disponível em `http://localhost:5173`.**

---

## 2. Ambiente de Produção

Use este modo para testar a imagem final que irá para o servidor. O Frontend é compilado e servido pelo Backend.

### Passo 1: Garantir Dependências Externas

Em produção, a aplicação espera que o **LDAP** e o **Banco AGHU** já existam na rede. Para testar localmente, mantenha o
docker-compose de dev rodando (pois ele provê esses serviços):

```bash
podman-compose -f docker-compose.dev.yml -p quimio_dev up
```

### Passo 2: Construção e Execução da Aplicação

Este comando constrói a imagem e inicia o container `quimio_app_prod` e seu banco de dados `quimio_db_prod`.

```bash
podman-compose -f docker-compose.prod.yml -p quimio_prod up --build
```

### Passo 3: Acesso

* A aplicação completa (Front + Back) estará disponível em: **`http://localhost:8000`**
* **Nota:** Não é necessário rodar `npm run dev` ou `uvicorn` separadamente.
* **Seed:** O script `seed_prod.py` roda automaticamente na inicialização, criando as configurações básicas se o banco
  de dados estiver vazio.

---

## Resumo de Comandos

| Ação                  | Comando                                                                                   |
|-----------------------|-------------------------------------------------------------------------------------------|
| **Iniciar Infra Dev** | `podman-compose -f docker-compose.yml -f docker-compose.dev.yml -p quimio_dev up --build` |
| **Resetar Banco Dev** | `podman rm -f db_app && podman volume rm quimio_dev_postgres_app_data`                    |
| **Iniciar Produção**  | `podman-compose -f docker-compose.prod.yml -p quimio_prod up --build`                     |
| **Parar Produção**    | `podman-compose -f docker-compose.prod.yml -p quimio_prod down`                           |
