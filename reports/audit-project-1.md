================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 3 | LOW: 3

## Findings

### [CRITICAL] Injection
File: models.py:28-299
Description: Consultas de produto, usuário, pedido e busca concatenam id, nome, e-mail, senha e termo de busca direto no SQL (`"WHERE id = " + str(id)`, `LIKE '%" + termo + "%'`).
Impact: Qualquer campo de texto vira SQL Injection. Dá para ler ou alterar as quatro tabelas.
Recommendation: Playbook 2 — placeholders `?` e lista de parâmetros, inclusive no LIKE.

### [CRITICAL] Sensitive data exposure
File: app.py:59-78
Description: `POST /admin/query` executa o SQL enviado no corpo, inclusive comandos que não são SELECT.
Impact: Escrita arbitrária no banco por quem alcança a rota.
Recommendation: Playbook 12 — manter a rota e recusar a execução.

### [CRITICAL] Hardcoded credentials
File: app.py:7, database.py:76-78
Description: `SECRET_KEY` fixa em `minha-chave-super-secreta-123`. O seed grava `admin123`, `123456` e `senha123` em texto puro.
Impact: O segredo da aplicação e as senhas iniciais vazam com o código-fonte.
Recommendation: Playbook 1 e 4 — config por ambiente e hash na gravação.

### [CRITICAL] God class / god module
File: models.py:1-314
Description: Um único módulo faz SQL, regra de estoque, desconto de vendas e serialização dos quatro domínios.
Impact: Não há como testar um domínio sem carregar o arquivo inteiro. Qualquer mudança atravessa produto, usuário e pedido.
Recommendation: Playbook 3 — models, controllers e views por domínio.

### [CRITICAL] Sensitive data exposure
File: controllers.py:289, models.py:79-86
Description: `GET /health` devolve a secret key, `debug: True` e o caminho do banco. `get_todos_usuarios` e `get_usuario_por_id` incluem a coluna `senha`.
Impact: Credencial da aplicação e senha dos usuários saem em resposta HTTP.
Recommendation: Playbook 11 — DTO público e health sem segredo.

### [HIGH] Global mutable state
File: database.py:4-10
Description: `db_connection` de módulo é reutilizada por todos os requests, com `check_same_thread=False`.
Impact: Estado compartilhado entre requisições e acoplamento que impede troca ou isolamento do banco.
Recommendation: Playbook 6 — conexão em `flask.g` e fechamento no teardown.

### [HIGH] Fat controller or fat route
File: controllers.py:24-255
Description: Os handlers validam, chamam o banco, disparam e-mail/SMS/push por `print` e montam o JSON. A validação de produto está copiada em criar e atualizar.
Impact: Regra de negócio presa na borda HTTP. O fluxo de pedido não tem serviço próprio.
Recommendation: Playbook 7 — controller orquestra, notificação sai para um serviço.

### [HIGH] Fat controller or fat route
File: app.py:47-78
Description: O entry point executa `DELETE` nas quatro tabelas e a query arbitrária. Não há autenticação nessas rotas nem na listagem de usuários e no relatório.
Impact: Operação administrativa fica no composition root e qualquer cliente chama reset, relatório e lista de usuários.
Recommendation: Playbook 7 e 12 — SQL fixo no model para o reset; a query arbitrária deixa de executar. As rotas públicas continuam sem header obrigatório para não quebrar o contrato.

### [MEDIUM] N+1 queries
File: models.py:171-233
Description: `get_pedidos_usuario` e `get_todos_pedidos` abrem uma consulta de itens por pedido e outra de produto por item.
Impact: O custo cresce com o número de pedidos. A listagem inteira repete o mesmo padrão duas vezes.
Recommendation: Playbook 5 — um JOIN e agrupamento em memória.

### [MEDIUM] Duplicated logic
File: controllers.py:24-96, models.py:12-21
Description: A checagem de nome, preço e estoque está duplicada. O dicionário do produto é remontado em várias funções.
Impact: Uma regra nova precisa ser editada em mais de um lugar e tende a divergir.
Recommendation: Playbook 7 — uma validação de criação e um serializador único.

### [MEDIUM] Missing centralized error handling
File: controllers.py:6-12
Description: Cada handler repete `except Exception` e devolve `str(e)`. Não existe error handler da aplicação.
Impact: Mensagem interna vaza para o cliente e o formato de erro não tem um único lugar.
Recommendation: Playbook 10 — middleware para exceção não prevista. Validação continua explícita no controller.

### [LOW] Magic numbers
File: models.py:256-262
Description: Faixas 10000, 5000 e 1000 e taxas 0.1, 0.05 e 0.02 definem o desconto do relatório sem nome.
Impact: A regra comercial não se explica lendo o código.
Recommendation: Playbook 9 — tabela de faixas nomeada.

### [LOW] Poor naming and debug noise
File: controllers.py:8, controllers.py:56
Description: O fluxo normal faz `print` de listagem, erro e login. `id = models.criar_produto(...)` sombreia o builtin.
Impact: Log barulhento e nome que esconde o identificador do produto.
Recommendation: Playbook 11 — logger e nome `produto_id` no código novo. O parâmetro de rota `id` permanece porque faz parte do contrato do Flask.

### [LOW] Poor naming and debug noise
File: controllers.py:285-288
Description: O health anuncia `ambiente: producao` e `debug: True` ao mesmo tempo, com `versao` e `db_path` chumbados.
Impact: A resposta operacional mente sobre o ambiente.
Recommendation: Playbook 1 — `ambiente` e versão vêm da config, sem flag de debug no JSON.

## Deprecated API Scan
Nenhuma assinatura do catálogo encontrada (sem `datetime.utcnow`, `Query.get`, `before_first_request` ou `new Buffer`).

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
