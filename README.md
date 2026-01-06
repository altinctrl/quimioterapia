# Sistema de Gestão de Quimioterapia

Este sistema é uma solução Full-Stack para o gerenciamento de sessões de quimioterapia, modernizando o fluxo de trabalho hospitalar e integrando-se com o sistema legado (AGHU).

## 🚀 Funcionalidades e Módulos

O sistema é dividido em módulos funcionais focados nas necessidades de médicos, enfermeiros e farmacêuticos.

### 📅 Agenda
Gerencia o fluxo diário de pacientes e a ocupação da clínica.
* **O que resolve:** Reforça regras de negócio durante o agendamento e centraliza a visualização e gerenciamento do status do paciente.
* **Recursos:** 
  * Visualização por data com navegação facilitada.
  * Filtros avançados por turno, status da farmácia e grupo de infusão.
  * Métricas em tempo real (total de pacientes, em infusão, concluídos, intercorrências).
  * Gestão de Tags e remarcação de horários.
  * Alteração de status com registro de justificativas para intercorrências ou suspensões.

### 💊 Prescrição
Interface para criação e validação segura de protocolos quimioterápicos.
* **O que resolve:** Reduz erros de cálculo e agiliza o processo de prescrição através de modelos pré-definidos.
* **Recursos:**
  * Cálculo automático de Superfície Corpórea (SC).
  * Sugestão inteligente de protocolo e ciclo baseada no histórico do paciente.
  * Carregamento de itens padrão de Pré-QT, QT e Pós-QT a partir de protocolos ou última prescrição realizada.
  * Geração de PDF e impressão da prescrição para assinatura física.

### 🧪 Farmácia
Módulo dedicado à preparação e controle de medicamentos.
* **O que resolve:** Melhora a comunicação entre farmácia e enfermagem sobre o preparo dos fármacos.
* **Recursos:**
  * Monitoramento de status: Pendente, Em Preparação, Pronta e Enviada.
  * Registro de previsão de entrega para otimização do início da infusão.
  * Métricas de produtividade da farmácia.

### 👤 Pacientes
Prontuário eletrônico focado na oncologia.
* **O que resolve:** Centraliza o histórico clínico, agendamentos e prescrições.
* **Recursos:**
  * Busca rápida por nome, CPF ou registro.
  * Histórico completo de agendamentos e prescrições anteriores.
  * Visualização do protocolo atual e ciclo vigente no cabeçalho do prontuário.
  * Importação de dados de pacientes (integração com AGHU).

### 📋 Relatórios e Ajustes
* **Relatórios:** Emissão de relatórios de fim de plantão e consumo de medicamentos por farmácia.
* **Protocolos:** Cadastro e edição de protocolos complexos, incluindo tempos de infusão e dias permitidos na semana.
* **Configurações:** Definição de horários de funcionamento, capacidade de vagas por grupo (Rápido/Médio/Longo) e gestão de tags.

---

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.10+ (FastAPI).
- **Frontend:** Vue.js 3, Vite, TypeScript, TailwindCSS, Pinia.
- **Banco de Dados:** PostgreSQL (Em container).
- **ORM/Migrações:** SQLAlchemy e Alembic.

---

## 📚 Documentação Técnica

Para aprofundamento, consulte a pasta `docs/`:

* **[Guia de Configuração](docs/SETUP.md):** Como preparar e iniciar a aplicação.
* **[Guia de Contribuição](docs/CONTRIBUTING.md):** Padrões de código, commits e fluxo de Git.
* **[Arquitetura do Sistema](docs/ARCHITECTURE.md):** Explicação das camadas, providers e decisões técnicas.
* **[Banco de Dados e Migrações](docs/DATABASE.md):** Comandos do Alembic e modelagem de dados.
* **[Autenticação](docs/AUTHENTICATION.md):** Como funciona a autenticação.