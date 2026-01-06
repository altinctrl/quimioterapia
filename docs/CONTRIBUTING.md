# Guia de Contribuição

Obrigado por se interessar em contribuir! Este documento define o fluxo de trabalho e os padrões que utilizamos para manter a qualidade do código.

## 1. Ciclo de Vida do Projeto

1. **Issues:** Desejável (mas não obrigatório) para discutir novas ideias ou reportar bugs antes da implementação.
2. **Desenvolvimento:** O trabalho é feito em branches específicos.
3. **Forks:** Se você **não** faz parte da equipe principal, por favor, realize um **Fork** do projeto para contribuir. Membros da equipe podem criar branches diretamente no repositório.
4. **Pull Request (PR):** **Obrigatório** para todas as alterações. Nenhuma mudança deve ser feita diretamente na `main`.
5. **Revisão:** Todo PR deve ser revisado e aprovado por outro membro antes do merge.

---

## 2. Nomenclatura de Branches e Padrão de Commits

Utilizamos prefixos para identificar o propósito do branch. O formato deve ser: `tipo/numero_da_issue-breve_descricao`.

O título de commits deve sempre começar com o verbo no **presente do indicativo** (ex: "adiciona", "corrige", "implementa"). Não use o infinitivo ("adicionar") ou o passado ("adicionado").

Utilize os prefixos abaixo tanto para nomear branches quanto para iniciar as mensagens de commit.

| Tipo         | Descrição                                                         | Exemplo de Mensagem                                  |
|--------------|-------------------------------------------------------------------|------------------------------------------------------|
| **feature**  | Nova funcionalidade                                               | `feature: adiciona filtro de data no relatório`      |
| **fix**      | Correção de erro                                                  | `fix: corrige erro de autenticação no Safari`        |
| **refactor** | Mudança no código que não altera o comportamento                  | `refactor: simplifica a lógica de validação`         |
| **reformat** | Mudança na formatação/estrutura do código (espaços, indentação)   | `reformat: ajusta indentação do módulo de pacientes` |
| **chore**    | Mudanças em documentação, ferramentas, build ou pacotes           | `chore: atualiza versão da biblioteca de logs`       |
| **test**     | Adição ou modificação de testes                                   | `test: implementa teste unitário para o agendamento` |
| **style**    | Mudanças de estilo visual e UI (CSS/HTML) que não afetam a lógica | `style: altera cor do botão de salvar para azul`     |

---

## 3. Como abrir uma Issue

Antes de codificar, verifique se já não existe uma issue para o problema. Caso contrário, abra uma nova seguindo este roteiro:

* **Título claro:** Resuma o problema ou sugestão.
* **Contexto:** Explique o "porquê" desta mudança.
* **Passos para reproduzir:** (Em caso de bugs).
* **Resultado esperado vs. Resultado atual.**

---

## 4. Pull Requests

Como ainda não possuímos pipeline de CI/CD, a atenção na revisão manual é redobrada:

* Certifique-se de que o código está funcionando localmente antes de abrir o PR.
* Descreva brevemente o que foi alterado.
* Se houver uma issue relacionada, utilize `Closes #numero_da_issue`.
