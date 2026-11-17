# Catálogo de anti-patterns

Escala usada em toda auditoria:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

Só reporte um item se o sinal estiver no código. A severidade abaixo é a padrão; suba um nível apenas quando o mesmo trecho também vaza segredo ou permite escrita arbitrária.

## 1. Hardcoded credentials — CRITICAL

Sinais: string literal atribuída a `SECRET_KEY`, `password`, `passwd`, `apiKey`, `token`, senha de SMTP, chave de gateway ou usuário de banco. Seed com senha em texto puro no código-fonte entra aqui.

Não é este item: porta, nome de host local, flag de debug.

Playbook: extrair configuração.

## 2. Injection — CRITICAL

Sinais: SQL, shell ou eval montado por concatenação ou interpolação com dado da request, da rota ou do corpo.

```text
"SELECT ... WHERE id = " + id
`SELECT ... WHERE email = '${email}'`
cursor.execute(f"DELETE FROM t WHERE id = {id}")
eval(, exec(, child_process com entrada do usuário
```

Consulta parametrizada (`?`, `%s` com tupla, query builder com bind) não é injection. `LIKE` com o valor inteiro passado como parâmetro também não é.

Playbook: parametrizar consultas.

## 3. God class / god module — CRITICAL

Sinais: um arquivo acumula pelo menos três destes papéis para mais de um domínio: schema ou conexão, regra de negócio, serialização HTTP, roteamento. Vale para `models.py` único, `AppManager`, `utils.js` que também guarda segredo e cache, ou um service que faz checkout, pagamento e HTTP.

Playbook: fatiar em MVC por domínio.

## 4. Sensitive data exposure — CRITICAL

Sinais: resposta JSON com `senha`, `password`, `pass`, `SECRET_KEY` ou número completo de cartão; `console.log` / `print` do PAN, da senha ou da chave; endpoint que executa SQL enviado pelo cliente (`/admin/query`, `exec(req.body.sql)`).

Playbook: serializar DTO público, desligar execução arbitrária, mascarar log.

## 5. Weak cryptography — HIGH

Sinais: senha comparada em texto puro; `hashlib.md5` ou `sha1` para senha; hash caseiro (`base64` em loop, reversível); token fixo no formato `fake-jwt-token-<id>` sem assinatura.

Playbook: hash adaptativo e token assinado. Não passe a exigir o token nas rotas que eram públicas.

## 6. Global mutable state — HIGH

Sinais: conexão, cache ou acumulador em variável de módulo (`db_connection = None`, `globalCache = {}`, `totalRevenue = 0`) reutilizada por todos os requests. `check_same_thread=False` reforça o achado.

Playbook: escopo por request (`flask.g`) ou conexão única encapsulada num módulo de infraestrutura, sem mutação solta.

## 7. Fat controller or fat route — HIGH

Sinais: a função de rota valida regra, calcula total, altera estoque, dispara e-mail e monta SQL. Em projeto que já tem model, a rota repete a regra que o model já tem (`is_overdue` ignorado, validação copiada).

Playbook: rota fina + controller. Model fica com persistência e invariante.

## 8. N+1 queries — MEDIUM

Sinais: consulta de filhos dentro de `for` / `forEach` sobre pais. Exemplos: para cada pedido, buscar itens; para cada item, buscar produto; para cada curso, buscar matrículas e depois usuário e pagamento; `User.query.get` dentro do loop de tasks.

Playbook: `JOIN`, `IN (...)` ou eager load (`joinedload`).

## 9. Duplicated logic — MEDIUM

Sinais: o mesmo bloco de validação, serialização ou cálculo de atraso copiado em criar/atualizar ou em dois arquivos. Constante definida (`MIN_TITLE_LENGTH`) e o literal repetido na rota também contam.

Playbook: uma função ou o método que já existe no model.

## 10. Missing centralized error handling — MEDIUM

Sinais: `except:` nu, `except Exception` que devolve `str(e)` em toda rota, ausência de middleware de erro, callback com erro ignorado (`function (err)` sem `if (err)`).

Playbook: middleware único e erro de domínio explícito.

## 11. Partial write / callback pyramid — MEDIUM

Sinais: vários `INSERT` seguidos sem transação; pirâmide de callbacks (`db.get` dentro de `db.get`); `DELETE` de pai sem limpar filhos quando o domínio exige consistência (matrícula e pagamento órfãos).

Playbook: `async/await` e transação em torno do fluxo de escrita.

## 12. Deprecated or obsolete API — MEDIUM

Rode esta varredura em todo projeto. Cada ocorrência vira finding (pode agrupar várias APIs no mesmo finding se a severidade for a mesma). Se nada casar, escreva a nota de varredura.

| Assinatura | Substituto |
|---|---|
| `datetime.utcnow` e `datetime.utcfromtimestamp` | `datetime.now(timezone.utc)` (grave naive só se o schema atual for naive) |
| `Model.query.get(` / `Session.query.get(` | `db.session.get(Model, id)` |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | remover; a flag saiu no Flask-SQLAlchemy 3 |
| `new Buffer(` | `Buffer.from` / `Buffer.alloc` |
| `req.param(` | `req.params` / `req.query` / `req.body` |
| `app.del(` | `app.delete` |
| `res.sendfile(` | `res.sendFile` |
| `flask.before_first_request` | inicialização explícita na factory |
| `hashlib.md5` / `hashlib.sha1` para senha | ver item 5 (se já reportado como criptografia fraca, cite aqui só na varredura, sem segundo finding) |

Playbook: substituir API obsoleta.

## 13. Magic numbers — LOW

Sinais: limite de tamanho, faixa de prioridade, percentual de desconto, prefixo de cartão ou janela de dias literais no meio da regra, sem constante nomeada.

Playbook: constante nomeada no domínio ou na config.

## 14. Poor naming and debug noise — LOW

Sinais: variáveis de uma letra para conceito de negócio (`u`, `e`, `p`, `cid`, `cc`); nome que sombreia builtin (`id = ...`); `print` / `console.log` de debug no fluxo normal; import não usado; flag que mente sobre o ambiente (`ambiente: producao` com `debug: True`).

Playbook: renomear no código novo e trocar debug por logger. Não renomeie o contrato JSON (`usr`, `eml`, `c_id`) se o cliente já envia esses campos.
