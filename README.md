# Refatoração arquitetural automatizada

Skill `refactor-arch` que analisa um backend, audita anti-patterns de MVC, SOLID e segurança e refatora o projeto para Model-View-Controller sem prender a receita a uma linguagem. Os três projetos deste repositório foram a prova: dois em Python/Flask, com graus diferentes de organização, e um em Node.js/Express.

A skill está em `.claude/skills/refactor-arch/` dentro de cada projeto (convenção do Claude Code). `SKILL.md` conduz as três fases. O conhecimento de domínio fica em `references/`.

## Análise manual

A leitura abaixo foi feita antes da skill, no código original. A Fase 2 precisava reencontrar estes problemas a partir do catálogo, não de uma lista fechada por projeto.

### code-smells-project (Python/Flask, e-commerce)

| Severidade | Problema | Onde | Por que importa |
|---|---|---|---|
| CRITICAL | SQL concatenado em produto, usuário, pedido e busca | `models.py` | Um nome com aspas vira comando no SQLite. |
| CRITICAL | `SECRET_KEY` e senhas de seed no fonte | `app.py`, `database.py` | O segredo da aplicação e as senhas iniciais viajam com o repositório. |
| CRITICAL | God module com os quatro domínios | `models.py` | Banco, regra de estoque e serialização no mesmo arquivo. |
| MEDIUM | N+1 ao listar pedidos | `models.py`, laços de itens e produtos | A listagem dispara uma consulta por pedido e outra por item. |
| MEDIUM | Validação de produto copiada | `controllers.py`, criar e atualizar | A mesma regra diverge na hora de mudar um limite. |
| LOW | Faixas de desconto literais | `models.py`, relatório de vendas | 10000, 5000, 0.1 e 0.05 não dizem o que são. |
| LOW | `print` de debug e `id` sombreando builtin | `controllers.py` | O fluxo normal polui a saída e o nome mente. |

### ecommerce-api-legacy (Node.js/Express, LMS com checkout)

| Severidade | Problema | Onde | Por que importa |
|---|---|---|---|
| CRITICAL | Chave de gateway, senha de banco e SMTP no fonte | `src/utils.js` | Credencial de produção dentro do módulo de "utilitários". |
| CRITICAL | `AppManager` faz schema, HTTP, cobrança e auditoria | `src/AppManager.js` | Não existe camada para testar o checkout sem subir a classe inteira. |
| HIGH | Hash caseiro de senha e seed em texto puro | `src/utils.js` | O valor guardado em `pass` não é um hash de verdade. |
| MEDIUM | Relatório financeiro em callbacks aninhados | `src/AppManager.js` | Uma query por curso, por matrícula, por usuário e por pagamento. |
| MEDIUM | Delete de usuário deixa matrícula e pagamento | `src/AppManager.js` | A própria resposta admite o banco sujo. |
| LOW | Parâmetros `u`, `e`, `p`, `cid`, `cc` | checkout | O fluxo de pagamento não se lê. |
| LOW | Aprovação do cartão é "começa com 4" | checkout | Número mágico no meio do callback. |

### task-manager-api (Python/Flask, já com pastas)

| Severidade | Problema | Onde | Por que importa |
|---|---|---|---|
| CRITICAL | `SECRET_KEY` fixa e MD5 com a senha saindo no JSON | `app.py`, `models/user.py` | Segredo no entry point e hash da senha na resposta de login. |
| HIGH | Rotas gordas, sem controller | `routes/` | A pasta `models/` existe, mas a regra continua na rota. |
| MEDIUM | N+1 em tasks, relatório e categorias | `routes/task_routes.py`, `routes/report_routes.py` | Cada task busca usuário e categoria de novo. |
| MEDIUM | `datetime.utcnow`, `Query.get` e `SQLALCHEMY_TRACK_MODIFICATIONS` | models, rotas, `app.py` | API obsoleta no runtime atual do Flask-SQLAlchemy 3. |
| LOW | Constantes definidas e literais repetidos | `utils/helpers.py` contra as rotas | `MIN_TITLE_LENGTH` existe e a rota continua usando `3`. |
| LOW | Import morto e serviço de e-mail nunca chamado | `app.py`, `services/notification_service.py` | A leitura sugere dependência que o fluxo não tem. |

## Construção da skill

### Decisões de design

`SKILL.md` só diz o que fazer em cada fase e quando parar. Ele não contém o catálogo. Isso deixa o prompt curto e obriga o agente a abrir o arquivo certo:

| Arquivo | Fase | Conteúdo |
|---|---|---|
| `references/project-analysis.md` | 1 | Sinais de linguagem, framework, banco, domínio e forma da arquitetura |
| `references/antipattern-catalog.md` | 2 | 14 anti-patterns, severidade e sinal objetivo de detecção |
| `references/audit-report-template.md` | 2 | Formato do relatório e a pergunta de confirmação |
| `references/mvc-guidelines.md` | 3 | Responsabilidade de cada camada e o layout por stack |
| `references/refactoring-playbook.md` | 3 | 12 transformações com antes/depois em Python e JavaScript |

A Fase 2 termina com `Proceed with refactoring (Phase 3)? [y/n]` e não altera código-fonte antes do sim. Nesta entrega o sim já estava no pedido: executar as três fases nos três projetos.

### O que entrou no catálogo

Entrou o que aparecia nos três códigos e o que a escala do desafio pede para uma skill genérica:

- CRITICAL: credencial no fonte, injection, god class, vazamento de segredo ou de senha, SQL arbitrário
- HIGH: criptografia fraca, estado global mutável, rota/controller gordo, token falso
- MEDIUM: N+1, duplicação, erro sem middleware, escrita parcial, API deprecated
- LOW: número mágico, nome ruim, debug e código morto

A varredura de API obsoleta é obrigatória em todo projeto. Ausência vira nota, não finding inventado. No task manager ela achou `datetime.utcnow`, `Query.get` e `SQLALCHEMY_TRACK_MODIFICATIONS`. Nos outros dois, nenhuma assinatura do catálogo.

### Como a skill fica agnóstica

A Fase 1 decide a stack por manifesto e import (`requirements.txt` + Flask, `package.json` + Express, e a tabela também cobre Go, Java, C#, PHP e Ruby). O playbook mostra o mesmo padrão nas duas linguagens destes projetos. A Fase 3 não impõe a árvore do Flask no Node:

- monolito Python ganhou `models/`, `views/`, `controllers/`, `config/` e `middlewares/`
- Node manteve `src/` e o `npm start`
- task manager já tinha `routes/`; a skill afinou essa pasta e criou `controllers/`, em vez de renomear diretório por estética

O contrato HTTP manda mais que o exemplo do playbook. Método, caminho, status de sucesso e campos que o cliente já envia (`usr`, `eml`, `c_id`) ficaram. Senha, secret key e SQL arbitrário saíram da resposta.

### Dificuldades

O task manager parecia organizado e ainda assim a rota fazia o trabalho do controller. A skill trata "tem pasta models" como arquitetura parcial, não como MVC pronto.

O checkout em Node aprovava o cartão com um literal e registrava o PAN no log. Tirar o log sem mudar `card.startsWith("4")` foi o jeito de corrigir o vazamento e manter o `api.http` válido.

`datetime.utcnow` virou `datetime.now(timezone.utc)` sem fuso, porque as colunas já guardam datetime ingênuo. Misturar aware e naive quebraria o cálculo de atraso.

O hash padrão do Werkzeug neste ambiente é `scrypt`, não `pbkdf2`. O model grava `pbkdf2:sha256` e ainda aceita `scrypt` e o MD5 antigo, para um banco que já existia continuar autenticando.

## Resultados

### Contagem da Fase 2

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|
| code-smells-project | 5 | 3 | 3 | 3 | 14 |
| ecommerce-api-legacy | 3 | 3 | 4 | 2 | 12 |
| task-manager-api | 3 | 2 | 4 | 2 | 11 |

Os relatórios completos estão em `reports/audit-project-1.md`, `reports/audit-project-2.md` e `reports/audit-project-3.md`. Os cinco problemas da análise manual de cada projeto aparecem neles.

### Antes e depois

**code-smells-project**

Antes: `app.py`, `controllers.py`, `models.py`, `database.py`.

Depois:

```text
app.py
config/settings.py
database.py
models/produto_model.py
models/usuario_model.py
models/pedido_model.py
controllers/
views/routes.py
middlewares/error_handler.py
services/notification_service.py
utils/passwords.py
```

**ecommerce-api-legacy**

Antes: `src/app.js`, `src/AppManager.js`, `src/utils.js`.

Depois:

```text
src/app.js
src/config/settings.js
src/database.js
src/models/userModel.js
src/models/courseModel.js
src/models/enrollmentModel.js
src/controllers/
src/views/routes.js
src/middlewares/errorHandler.js
src/services/paymentService.js
src/services/passwordService.js
```

**task-manager-api**

Antes: `models/`, `routes/` gordas, `services/`, `utils/`, config no `app.py`.

Depois: as mesmas pastas, rotas com uma delegação, `controllers/` por domínio (task, user, category, report), `config/settings.py` e `middlewares/error_handler.py`. Categorias saíram do blueprint de relatório.

### O que a refatoração mudou de propósito

- `POST /admin/query` responde 403 e não executa SQL.
- Listagem de usuário da loja e o `to_dict` do task manager não devolvem senha.
- Health da loja não devolve `secret_key`.
- Login do task manager devolve token HMAC (`id.assinatura`) em vez de `fake-jwt-token-<id>`.
- Delete de usuário no LMS também apaga matrículas e pagamentos. A rota continua em texto, status 200.

Criar produto, login `admin@loja.com` / `admin123`, checkout do `api.http` e as rotas do task manager seguem os mesmos caminhos e status de sucesso.

### Checklist de validação

Os três projetos fecharam o mesmo checklist.

#### Fase 1 — Análise

- [x] Linguagem detectada corretamente
- [x] Framework detectado corretamente
- [x] Domínio da aplicação descrito corretamente
- [x] Número de arquivos analisados condiz com a realidade (4, 3 e 15)

#### Fase 2 — Auditoria

- [x] Relatório segue o template dos arquivos de referência
- [x] Cada finding tem arquivo e linhas do código original
- [x] Findings ordenados de CRITICAL para LOW
- [x] Mínimo de 5 findings (14, 12 e 11)
- [x] Varredura de API deprecated incluída (achados só no task manager; nos outros dois a nota registra a ausência)
- [x] A Fase 2 pede confirmação antes de editar. Nesta execução o pedido já autorizava a Fase 3; a resposta `y` está no fim de cada relatório

#### Fase 3 — Refatoração

- [x] Estrutura de diretórios segue MVC, adaptada à stack
- [x] Configuração em `config/settings`, com `.env.example` e sem segredo no fonte
- [x] Models isolam o acesso a dados
- [x] Views ou routes só encaminham
- [x] Controllers concentram o fluxo HTTP
- [x] Error handler centralizado
- [x] Entry point claro (`python app.py` e `npm start` iguais aos README de cada projeto)
- [x] Aplicação inicia sem erro
- [x] Endpoints originais respondem no fluxo feliz

### Logs depois da refatoração

Loja, `python app.py` na porta 5000:

```text
==================================================
SERVIDOR INICIADO
Rodando em http://localhost:5000
==================================================
 * Running on http://127.0.0.1:5000
```

```text
GET /health
{"ambiente":"development","counts":{"pedidos":0,"produtos":10,"usuarios":3},"database":"connected","status":"ok","versao":"1.0.0"}
```

`GET /produtos` devolveu 10 itens. Não há `secret_key` no health.

LMS, `npm start` na porta 3000:

```text
LMS API rodando na porta 3000...
[LOG] Checkout concluído para usuário 2: Docker
```

```text
POST /api/checkout
{"msg":"Sucesso","enrollment_id":2}

GET /api/admin/financial-report
[{"course":"Clean Architecture","revenue":997,"students":[{"student":"Leonan","paid":997}]},{"course":"Docker","revenue":497,"students":[{"student":"Guilherme","paid":497}]}]
```

O log do checkout não contém cartão nem chave. Cartão `5111...` continua respondendo `400 Pagamento recusado`. Curso inexistente continua `404`.

Task manager, `python seed.py` e `python app.py` na porta 5001 neste teste (o padrão do `.env.example` é 5000):

```text
Seed concluído com sucesso!
  3 usuários
  4 categorias
  10 tasks
 * Running on http://127.0.0.1:5001
```

`GET /tasks` devolveu 10 itens. `POST /login` com `joao@email.com` / `1234` respondeu 200, com `token` assinado e sem o campo `password`.

### Comportamento em stacks diferentes

No monolito Flask a Fase 3 criou a árvore inteira e apagou `models.py` e `controllers.py`, porque um módulo e um pacote com o mesmo nome não convivem.

No Express a mesma skill não procurou `requirements.txt`. O relatório saiu com JavaScript + Express, banco em memória e tabelas `users`, `courses`, `enrollments`, `payments`, `audit_logs`. O entry point continuou `src/app.js`.

No task manager a Fase 1 marcou arquitetura parcial. A Fase 3 não reescreveu o schema nem trocou o nome das pastas. Entrou controller, config e handler de erro, e as rotas que já existiam ficaram finas. `Query.get` e `utcnow` saíram. Os endpoints de task, usuário, categoria e relatório continuaram respondendo.

## Como executar

### Pré-requisitos

- Python 3.11+ e Node.js 20+ (aqui: Python 3.11.9 e Node.js 24.13.1)
- Skill no formato do Claude Code: pasta `.claude/skills/refactor-arch/` e invocação `claude "/refactor-arch"`
- Para repetir a skill numa máquina nova, o Claude Code precisa estar instalado e autenticado. Nesta máquina o comando `claude` não está no PATH. As três fases foram executadas por um agente lendo o `SKILL.md` e os `references/`, que é o contrato da skill. Os relatórios em `reports/` são a saída da Fase 2; o código de cada projeto é a saída da Fase 3.

O `.env.example` de cada projeto é carregado se a variável ainda não existir. Dá para subir sem criar `.env`. Em produção, exporte `SECRET_KEY` (e, no LMS, `PORT` e `PAYMENT_GATEWAY_KEY`) antes do processo.

### Ordem sugerida

1. Ler um projeto e o catálogo em `.claude/skills/refactor-arch/references/antipattern-catalog.md`.
2. Invocar a skill na pasta do projeto.
3. Conferir o relatório da Fase 2 antes de aceitar a Fase 3.
4. Subir a aplicação e percorrer o fluxo feliz.

### Comandos da skill

```bash
cd code-smells-project
claude "/refactor-arch"

cd ../ecommerce-api-legacy
claude "/refactor-arch"

cd ../task-manager-api
claude "/refactor-arch"
```

A pasta da skill já está copiada nos três projetos.

### Subir e validar o código refatorado

Loja:

```bash
cd code-smells-project
pip install -r requirements.txt
python app.py
```

`GET http://localhost:5000/health`, `GET /produtos`, `POST /login` com `admin@loja.com` e `admin123`.

LMS:

```bash
cd ecommerce-api-legacy
npm install
npm start
```

Os corpos estão em `api.http`. Checkout com cartão `4111...` retorna 200. Cartão que não começa com `4` retorna 400.

Task manager:

```bash
cd task-manager-api
pip install -r requirements.txt
python seed.py
python app.py
```

`GET /tasks`, `GET /reports/summary`, `POST /login` com `joao@email.com` e `1234`. A resposta do login não traz `password`.

Os dois Flask usam a porta 5000 por padrão. Suba um de cada vez, ou exporte `PORT` antes.
