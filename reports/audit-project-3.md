================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.0.0 + Flask-SQLAlchemy 3.1.1
Dependencies:  flask-cors 4.0.0, marshmallow 3.20.1, requests 2.31.0, python-dotenv 1.0.0
Domain:        Task Manager API (tasks, usuários, categorias, relatórios)
Architecture:  Parcial — models, routes, services e utils existem, mas a rota ainda valida, consulta e serializa
Source files:  15 files analyzed
DB tables:     tasks, users, categories
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask
Files:   15 analyzed | ~1156 lines of code

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] Hardcoded credentials
File: app.py:13
Description: `SECRET_KEY` está fixa em `super-secret-key-123` no entry point.
Impact: Quem lê o fonte assina sessão ou token com o mesmo segredo do laboratório.
Recommendation: Playbook 1 — `config/settings.py` e `.env.example`.

### [CRITICAL] Weak cryptography
File: models/user.py:16-32
Description: `set_password` grava MD5 sem salt. `to_dict` inclui `password`, e login, criação e detalhe de usuário usam esse método.
Impact: A senha sai na API e o hash não resiste a uma tabela pré-calculada.
Recommendation: Playbook 4 — `generate_password_hash` (pbkdf2) e DTO sem a senha. MD5 antigo ainda é aceito na leitura para banco já existente.

### [CRITICAL] Hardcoded credentials
File: services/notification_service.py:7-10
Description: SMTP usa `taskmanager@gmail.com` e senha `senha123` no construtor.
Impact: Credencial de e-mail no fonte. O serviço nem é chamado pelas rotas, mas o segredo já está commitado.
Recommendation: Playbook 1 — host, usuário e senha vêm da config. Sem usuário configurado, o envio não tenta login.

### [HIGH] Fat controller or fat route
File: routes/task_routes.py:11-299, routes/user_routes.py:10-211, routes/report_routes.py:12-223
Description: Não existe camada de controller. Cada rota valida, consulta, calcula atraso e monta o JSON. `Task.is_overdue` e `process_task_data` existem e não são usados.
Impact: A separação models/routes é só de pasta. Regra de task está na borda HTTP.
Recommendation: Playbook 7 — `routes/` fica com uma linha; `controllers/` recebe o fluxo. Não renomear `routes/` para `views/`.

### [HIGH] Weak cryptography
File: routes/user_routes.py:207-211
Description: O login devolve `fake-jwt-token-` mais o id. Nenhuma rota confere esse valor.
Impact: O token não prova identidade. Qualquer cliente fabrica o mesmo string.
Recommendation: Playbook 4 — HMAC com a `SECRET_KEY`. As rotas que eram públicas continuam sem exigir o header.

### [MEDIUM] N+1 queries
File: routes/task_routes.py:41-57, routes/report_routes.py:53-68, routes/report_routes.py:163
Description: A listagem de tasks busca usuário e categoria por item. O relatório percorre os usuários e, para cada um, busca as tasks. Cada categoria dispara um `COUNT` próprio.
Impact: A listagem e o summary degradam com o volume de tasks e usuários.
Recommendation: Playbook 5 — `joinedload` na listagem e `GROUP BY` no relatório e nas categorias.

### [MEDIUM] Duplicated logic
File: routes/task_routes.py:30-39, routes/user_routes.py:171-180, models/task.py:50-60
Description: A regra de atraso (data passada e status diferente de done/cancelled) está no model e copiada na listagem, no detalhe, nas tasks do usuário e no relatório. A serialização da task também é reescrita na rota em vez de `to_dict`.
Impact: Uma mudança de status válido precisa ser caçada em vários arquivos.
Recommendation: Playbook 7 — `task.is_overdue()` e `to_dict()` como único caminho.

### [MEDIUM] Deprecated or obsolete API
File: app.py:12, models/task.py:15-16, models/user.py:14, models/category.py:11, routes/task_routes.py:42, routes/user_routes.py:29, routes/report_routes.py:105
Description: `datetime.utcnow` aparece em models, seed, rotas, relatório e no serviço de e-mail. `Model.query.get` é o acesso por id nas rotas. `SQLALCHEMY_TRACK_MODIFICATIONS` está ligado no Flask-SQLAlchemy 3, onde a flag saiu.
Impact: Warning hoje e quebra quando o runtime remover `utcnow` ou o legacy Query.get.
Recommendation: Playbook 8 — `datetime.now(timezone.utc)` gravado como naive para não misturar com o schema atual, `db.session.get` e remoção da flag.

### [MEDIUM] Fat controller or fat route
File: routes/report_routes.py:157-223, routes/task_routes.py:62
Description: CRUD de categoria mora no blueprint de relatório. Vários handlers usam `except:` nu e engolem o erro.
Impact: Categoria não tem dono claro. Falha de banco vira 500 genérico sem registro da causa no código da rota.
Recommendation: Playbook 7 e 10 — blueprint de categoria, `except Exception` com rollback, e error handler da aplicação.

### [LOW] Magic numbers
File: utils/helpers.py:110-116, routes/task_routes.py:96-114
Description: `MIN_TITLE_LENGTH`, `MAX_TITLE_LENGTH`, `MIN_PASSWORD_LENGTH` e `DEFAULT_PRIORITY` existem no helper, mas as rotas repetem 3, 200, 4 e 5. A janela do relatório é o literal 7.
Impact: A constante e o literal divergem assim que alguém muda só um dos lados.
Recommendation: Playbook 9 — a rota usa as constantes, inclusive `REPORT_WINDOW_DAYS`.

### [LOW] Poor naming and debug noise
File: app.py:7, routes/task_routes.py:7, services/notification_service.py:4
Description: `app.py` importa `os`, `sys` e `json` sem uso. A rota de task importa `json`, `os`, `sys` e `time` sem uso. O serviço de notificação não é chamado por nenhuma rota.
Impact: Ruído na leitura e dependência aparente que o fluxo não tem.
Recommendation: Remover o import morto. O serviço permanece, lendo SMTP da config, porque o domínio de notificação continua válido.

## Deprecated API Scan
Ocorrências registradas no finding de API obsoleta: `datetime.utcnow`, `Query.get` e `SQLALCHEMY_TRACK_MODIFICATIONS`. `hashlib.md5` foi classificado como criptografia fraca, sem segundo finding.

================================
Total: 11 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
