---
name: refactor-arch
description: Analisa linguagem, framework e arquitetura de um backend, gera um relatório de auditoria com anti-patterns classificados por severidade (arquivo e linha) e refatora o projeto para MVC preservando o contrato HTTP. Use quando o usuário invocar /refactor-arch, pedir auditoria arquitetural, detecção de code smells, ou refatoração para Model-View-Controller em qualquer stack.
---

# refactor-arch

Skill agnóstica de tecnologia para analisar, auditar e refatorar um backend para MVC. O conhecimento de domínio está nos arquivos de `references/`. Leia cada arquivo no início da fase que o utiliza. Não improvise severidade, formato de relatório nem estrutura alvo.

Trabalhe no projeto cujo diretório atual contém esta skill. Não assuma Python, Flask, Node ou Express até a Fase 1 confirmar a stack.

## Regras que valem nas 3 fases

- Preserve o comando de subida já existente (`python app.py`, `npm start`, ou o script equivalente).
- Preserve método HTTP, caminho, status de sucesso e campos essenciais do JSON de cada endpoint público.
- Correções de segurança podem remover segredos, senhas e hashes do corpo da resposta. Não passe a exigir header de autenticação em rota que antes era pública.
- Consultas ao banco usam parâmetros vinculados. Segredos saem do código-fonte e entram em variáveis de ambiente.
- Não modifique código-fonte da aplicação nas Fases 1 e 2. Escrever o relatório em `reports/` não conta como refatoração.
- Se o pedido do usuário já autorizou a Fase 3, registre a confirmação e continue. Caso contrário, pare ao final da Fase 2 e espere `y` ou `n`. `n` encerra a skill sem alterar arquivos.

## Fase 1 — Análise

Leia [references/project-analysis.md](references/project-analysis.md) e siga as heurísticas. Não use um detector fixo de uma linguagem só.

Imprima exatamente este bloco, preenchido com o que foi detectado:

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework e versão, se houver>
Dependencies:  <dependências diretas relevantes>
Domain:        <domínio de negócio em uma linha>
Architecture:  <como as responsabilidades estão organizadas hoje>
Source files:  <N> files analyzed
DB tables:     <tabelas ou "não identificado">
================================
```

Conte arquivos de código da aplicação. Ignore `node_modules`, `.venv`, lockfiles, bancos e a própria pasta `.claude`.

## Fase 2 — Auditoria

Leia [references/antipattern-catalog.md](references/antipattern-catalog.md) e [references/audit-report-template.md](references/audit-report-template.md).

1. Percorra o código e registre só anti-patterns que existem de fato, com arquivo e linhas reais.
2. Classifique com a escala do catálogo. Não promova um smell de nome para CRITICAL.
3. Ordene CRITICAL, HIGH, MEDIUM, LOW.
4. Rode a varredura de APIs deprecated do catálogo. Se não houver ocorrência, escreva a nota de varredura. Não invente finding.
5. Entregue no mínimo 5 findings, com pelo menos um CRITICAL ou HIGH, quando o código tiver esses problemas.
6. Imprima o relatório no template. Salve a mesma saída em `reports/audit-project-N.md` na raiz do repositório quando o usuário pedir o entregável do desafio (N = 1, 2 ou 3 conforme o projeto).
7. Termine com a pergunta abaixo e pare se a Fase 3 ainda não foi autorizada:

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Fase 3 — Refatoração

Leia [references/mvc-guidelines.md](references/mvc-guidelines.md) e [references/refactoring-playbook.md](references/refactoring-playbook.md).

1. Escolha o layout MVC do guia de acordo com a stack e com o que já existe. Projeto sem camadas ganha a árvore completa. Projeto que já tem `models/` e `routes/` recebe a camada que falta (em geral controllers, config e error handler) e as rotas existentes ficam finas. Não renomeie pastas só por estética.
2. Aplique um padrão do playbook para cada finding corrigido. Mantenha o contrato HTTP descrito acima.
3. Extraia configuração para `config/settings.*`, com leitura de ambiente e fallback em `.env.example` para o laboratório subir sem passo manual.
4. Centralize o tratamento de erro inesperado.
5. Remova o código antigo que foi substituído para não conviver com a versão god class.
6. Valide de verdade:
   - o processo importa ou escuta sem exceção;
   - cada endpoint original é chamado e responde o status de sucesso esperado no fluxo feliz;
   - um fluxo de escrita (criar recurso ou checkout) persiste e a leitura seguinte enxerga o efeito.
7. Imprima o bloco final:

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore real das pastas MVC>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Anti-patterns da auditoria corrigidos sem quebrar o contrato HTTP
================================
```

Se a validação falhar, corrija e rode de novo. Não declare a fase concluída com endpoint quebrado.
