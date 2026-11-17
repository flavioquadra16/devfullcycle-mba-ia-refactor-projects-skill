================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express 4.18.2
Dependencies:  express, sqlite3
Domain:        LMS API com checkout (usuários, cursos, matrículas, pagamentos)
Architecture:  Monolítica — AppManager concentra schema, pagamento, HTTP e auditoria
Source files:  3 files analyzed
DB tables:     users, courses, enrollments, payments, audit_logs
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Express
Files:   3 analyzed | ~181 lines of code

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] Hardcoded credentials
File: src/utils.js:1-7
Description: `dbPass`, `paymentGatewayKey` (`pk_live_1234567890abcdef`) e `smtpUser` estão no código. A chave não é usada para cobrar de verdade, mas está no repositório.
Impact: Segredo de produção no fonte. Qualquer cópia do projeto leva a chave embora.
Recommendation: Playbook 1 — `config/settings.js` lê ambiente e `.env.example`.

### [CRITICAL] God class / god module
File: src/AppManager.js:4-139
Description: A classe abre o SQLite em memória, cria o schema, faz seed, registra as rotas, cobra cartão, matricula e grava auditoria.
Impact: Checkout, relatório e exclusão de usuário só existem dentro do mesmo objeto. Não há model nem controller.
Recommendation: Playbook 3 — models, controllers, views e services sob `src/`.

### [CRITICAL] Sensitive data exposure
File: src/AppManager.js:45
Description: O checkout escreve no log o número completo do cartão e a chave do gateway.
Impact: PAN e segredo aparecem em stdout a cada compra.
Recommendation: Playbook 11 — logar só o id do usuário e o título do curso.

### [HIGH] Weak cryptography
File: src/utils.js:17-23
Description: `badCrypto` repete os dois primeiros caracteres do base64 da senha 10000 vezes e corta em 10. A senha do seed (`123`) fica em texto puro.
Impact: A senha armazenada é reversível na prática e não resiste a leitura do banco.
Recommendation: Playbook 4 — `crypto.scryptSync` com salt. O campo de entrada continua `pwd`.

### [HIGH] Global mutable state
File: src/utils.js:9-10
Description: `globalCache` e `totalRevenue` são estado de módulo. `logAndCache` grava o último checkout nesse objeto compartilhado.
Impact: Requests compartilham memória mutável. `totalRevenue` ainda é exportado sem ser atualizado.
Recommendation: Playbook 6 — remover o cache global. O efeito que a resposta não usa não precisa de variável de módulo.

### [HIGH] Fat controller or fat route
File: src/AppManager.js:80, src/AppManager.js:131
Description: `GET /api/admin/financial-report` e `DELETE /api/users/:id` não verificam identidade. O delete está no mesmo método que registra as rotas.
Impact: Relatório financeiro e exclusão de usuário são públicos. A rota mistura HTTP e SQL.
Recommendation: Playbook 7 — controller próprio. Não exigir header novo, para o cliente atual continuar chamando as rotas.

### [MEDIUM] N+1 queries
File: src/AppManager.js:83-128
Description: Para cada curso busca matrículas; para cada matrícula busca usuário e pagamento. `coursesPending` / `enrPending` tentam sincronizar os callbacks na mão.
Impact: Volume de queries explode com o catálogo e a resposta pode ser enviada mais de uma vez se a contagem falhar.
Recommendation: Playbook 5 — um SELECT com JOIN e agregação em memória, preservando `{ course, revenue, students }`.

### [MEDIUM] Partial write / callback pyramid
File: src/AppManager.js:37-77
Description: O checkout é uma pirâmide de `db.get` / `db.run`. Matrícula, pagamento e auditoria não estão na mesma transação.
Impact: Falha no meio deixa matrícula sem pagamento. O fluxo é difícil de ler e de tratar erro.
Recommendation: Playbook 10 — `async/await` e `BEGIN`/`COMMIT`.

### [MEDIUM] Partial write / callback pyramid
File: src/AppManager.js:131-136
Description: `DELETE /api/users/:id` apaga o usuário e a própria resposta admite que matrículas e pagamentos ficam órfãos. O erro do `run` é ignorado.
Impact: O relatório financeiro passa a apontar para usuário inexistente.
Recommendation: Playbook 10 — apagar pagamentos e matrículas do usuário na mesma transação. A rota continua respondendo 200 em texto.

### [MEDIUM] Missing centralized error handling
File: src/app.js:1-15
Description: `app.js` só monta o JSON, chama o manager e escuta a porta. Não há middleware de erro. Vários callbacks esquecem `err`.
Impact: Exceção assíncrona derruba o processo ou responde de forma inconsistente.
Recommendation: Playbook 10 — `asyncHandler` e error handler no fim da cadeia.

### [LOW] Poor naming and debug noise
File: src/AppManager.js:29-33
Description: O corpo do checkout é lido em `u`, `e`, `p`, `cid` e `cc`.
Impact: O fluxo de pagamento não se lê sem voltar no `api.http`.
Recommendation: Nomes internos `name`, `email`, `password`, `courseId` e `card`. Os campos JSON `usr`, `eml`, `pwd`, `c_id` e `card` permanecem.

### [LOW] Magic numbers
File: src/AppManager.js:46, src/utils.js:10
Description: Cartão aprovado é "começa com 4", literal no meio do callback. `totalRevenue` é estado morto.
Impact: A regra da adquirente não tem nome e o módulo exporta lixo.
Recommendation: Playbook 9 — `APPROVED_CARD_PREFIX` no serviço de pagamento. Remover `totalRevenue`.

## Deprecated API Scan
Nenhuma assinatura do catálogo encontrada (sem `new Buffer`, `req.param`, `app.del` ou `res.sendfile`). O estilo callback do `sqlite3` foi tratado como pirâmide de callbacks, não como API deprecated.

================================
Total: 12 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
