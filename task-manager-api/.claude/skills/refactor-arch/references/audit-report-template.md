# Template do relatório de auditoria

A Fase 2 imprime este formato e, quando o entregável do desafio pedir, grava o mesmo texto em `reports/audit-project-N.md`.

Regras de preenchimento:

- Findings ordenados por severidade: CRITICAL, HIGH, MEDIUM, LOW.
- Cada finding tem arquivo e linhas que existem no código analisado (uma linha, um intervalo ou uma lista curta).
- `Description`, `Impact` e `Recommendation` são obrigatórios.
- A recomendação aponta o padrão do playbook, sem aplicar a mudança nesta fase.
- O total do rodapé é a soma do summary.
- A varredura de API deprecated sempre aparece. Ocorrência vira finding. Ausência vira a nota, não um finding falso.

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework>
Dependencies:  <dependências>
Domain:        <domínio>
Architecture:  <arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <tabelas>
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome da pasta>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<linhas> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <título do catálogo>
File: <caminho>:<linhas>
Description: <o que o código faz>
Impact: <consequência de manutenção, teste ou segurança>
Recommendation: <padrão do playbook a aplicar>

### [HIGH] <título>
File: <caminho>:<linhas>
Description: ...
Impact: ...
Recommendation: ...

## Deprecated API Scan
<ocorrências já listadas como findings, ou "Nenhuma assinatura do catálogo encontrada.">

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Quando a Fase 3 já estiver autorizada, registre a resposta na linha seguinte:

```text
> y
```
