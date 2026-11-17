# Playbook de refatoração

Cada padrão mostra o sinal, a transformação e um antes/depois. Use o idioma do projeto. O contrato HTTP descrito nas guidelines manda mais do que o exemplo.

## 1. Extrair configuração

Antes (Python ou Node, o problema é o mesmo):

```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```

```javascript
const config = { paymentGatewayKey: "pk_live_1234567890abcdef", port: 3000 };
```

Depois:

```python
import os
from pathlib import Path

def load_env_file(path):
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_env_file(Path(".env"))
load_env_file(Path(".env.example"))
SECRET_KEY = os.environ["SECRET_KEY"]
PORT = int(os.environ.get("PORT", "5000"))
```

```javascript
const fs = require('fs');
function loadEnvFile(file) {
  if (!fs.existsSync(file)) return;
  for (const raw of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith('#') || !line.includes('=')) continue;
    const i = line.indexOf('=');
    const key = line.slice(0, i).trim();
    if (process.env[key] === undefined) process.env[key] = line.slice(i + 1).trim();
  }
}
loadEnvFile('.env');
loadEnvFile('.env.example');
const config = { port: Number(process.env.PORT || 3000), paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '' };
```

## 2. Parametrizar SQL

Antes:

```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("INSERT INTO usuarios (email, senha) VALUES ('" + email + "', '" + senha + "')")
```

Depois:

```python
row = db.execute("SELECT * FROM produtos WHERE id = ?", (id,)).fetchone()
db.execute(
    "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
    (nome, email, senha_hash, tipo),
)
```

```javascript
db.get('SELECT id FROM users WHERE email = ?', [email], callback);
```

Monte `WHERE 1=1` dinâmico só com placeholders e uma lista de parâmetros. Nunca interpole o termo do `LIKE`; interpole apenas o SQL fixo e vincule `'%' + termo + '%'`.

## 3. Fatiar god class em MVC

Antes: um módulo com SQL, regra de pedido e formatação para vários domínios; a rota chama esse módulo e ainda valida, notifica e devolve JSON.

Depois, por domínio:

- `models/produto_model.py` — consultas e mapa de linha para dict.
- `controllers/produto_controller.py` — valida o JSON e escolhe o status HTTP.
- `views/routes.py` — só registra o caminho.
- `services/notification_service.py` — log ou e-mail disparado pelo controller depois que o model confirma a escrita.

Apague o arquivo antigo quando o entry point deixar de importá-lo.

## 4. Senha e DTO público

Antes:

```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
return {'id': self.id, 'email': self.email, 'password': self.password}
```

```javascript
function badCrypto(pwd) {
  let hash = '';
  for (let i = 0; i < 10000; i++) hash += Buffer.from(pwd).toString('base64').substring(0, 2);
  return hash.substring(0, 10);
}
```

Depois:

```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, pwd):
    self.password = generate_password_hash(pwd)

def check_password(self, pwd):
    stored = self.password or ''
    if stored.startswith('pbkdf2:'):
        return check_password_hash(stored, pwd)
    return False

def to_dict(self):
    return {'id': self.id, 'email': self.email, 'role': self.role}
```

```javascript
const crypto = require('crypto');
function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(password, salt, 32).toString('hex');
  return `scrypt$${salt}$${hash}`;
}
```

Token no lugar de `fake-jwt-token-<id>`:

```python
import hmac, hashlib
def issue_token(user_id, secret):
    payload = str(user_id)
    sign = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f'{payload}.{sign}'
```

Não adicione middleware que rejeita pedido sem token se a rota era pública.

## 5. Trocar N+1 por JOIN ou eager load

Antes:

```python
for pedido in pedidos:
    itens = db.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(pedido["id"]))
    for item in itens:
        prod = db.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```

```javascript
courses.forEach((course) => {
  db.all('SELECT * FROM enrollments WHERE course_id = ?', [course.id], (_, enrollments) => {
    enrollments.forEach((enrollment) => {
      db.get('SELECT name FROM users WHERE id = ?', [enrollment.user_id], ...);
    });
  });
});
```

Depois:

```python
rows = db.execute(
    """
    SELECT p.id AS pedido_id, p.total, i.id AS item_id, i.quantidade, pr.nome AS produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
    """
).fetchall()
```

```javascript
const rows = await all(db, `
  SELECT c.id AS course_id, c.title, u.name AS student, p.amount, p.status
  FROM courses c
  LEFT JOIN enrollments e ON e.course_id = c.id
  LEFT JOIN users u ON u.id = e.user_id
  LEFT JOIN payments p ON p.enrollment_id = e.id
`);
```

```python
tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
```

Agrupe em memória pelo id do pai para manter a forma do JSON (`itens`, `students`).

## 6. Estado global vira escopo

Antes:

```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
    return db_connection
```

```javascript
let globalCache = {};
let totalRevenue = 0;
```

Depois:

```python
from flask import g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(settings.DATABASE_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db
```

Feche a conexão no teardown do request. Seed de banco em arquivo roda uma vez por processo, não de novo depois de um reset. Cache que ninguém lê sai. Efeito que a resposta não usa não precisa de variável de módulo.

## 7. Rota fina, controller com o fluxo

Antes:

```python
@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    if len(data.get('title', '')) < 3:
        return jsonify({'error': 'Título muito curto'}), 400
    task = Task(title=data['title'])
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201
```

Depois:

```python
@task_bp.route('/tasks', methods=['POST'])
def create_task():
    return task_controller.create_task()
```

```python
def create_task():
    data = request.get_json(silent=True)
    if not data or not data.get('title'):
        return jsonify({'error': 'Título é obrigatório'}), 400
    if len(data['title']) < MIN_TITLE_LENGTH:
        return jsonify({'error': 'Título muito curto'}), 400
    task = Task(title=data['title'].strip())
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201
```

Copie a mensagem de erro já publicada. Não "melhore" o texto no fluxo feliz nem no 400 que o cliente já trata.

## 8. Substituir API deprecated

Antes:

```python
created_at = db.Column(db.DateTime, default=datetime.utcnow)
user = User.query.get(user_id)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
```

```javascript
const secret = new Buffer(req.body.token);
```

Depois:

```python
def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

created_at = db.Column(db.DateTime, default=utc_now)
user = db.session.get(User, user_id)
```

```javascript
const secret = Buffer.from(req.body.token);
```

`replace(tzinfo=None)` só quando a coluna já guarda datetime ingênuo. Não misture aware e naive na comparação de atraso.

Se o finding de criptografia fraca já cobriu `md5`, não crie um segundo patch só para repetir a troca.

## 9. Constante no lugar de número mágico

Antes:

```python
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
```

```javascript
let status = cc.startsWith('4') ? 'PAID' : 'DENIED';
```

Depois:

```python
DISCOUNT_TIERS = ((10000, 0.10), (5000, 0.05), (1000, 0.02))

def discount_for(amount):
    for threshold, rate in DISCOUNT_TIERS:
        if amount > threshold:
            return amount * rate
    return 0
```

```javascript
const APPROVED_CARD_PREFIX = '4';
function charge(cardNumber) {
  return String(cardNumber).startsWith(APPROVED_CARD_PREFIX) ? 'PAID' : 'DENIED';
}
```

A regra de negócio permanece. Só o literal ganha nome.

## 10. Middleware de erro e transação

Antes: cada rota com `except Exception as e: return jsonify({'erro': str(e)}), 500`, ou vários inserts sem `BEGIN`.

Depois:

```python
def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_unexpected(exc):
        app.logger.exception('erro nao tratado')
        return jsonify({'erro': 'Erro interno', 'sucesso': False}), 500
```

```javascript
function asyncHandler(fn) {
  return (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
}
function errorHandler(err, req, res, next) {
  if (res.headersSent) return next(err);
  res.status(500).send('Erro interno');
}
```

Escrita com mais de uma tabela:

```python
try:
    db.execute('INSERT INTO pedidos ...', params)
    db.execute('INSERT INTO itens_pedido ...', item)
    db.commit()
except Exception:
    db.rollback()
    raise
```

```javascript
await run(db, 'BEGIN');
try {
  await run(db, 'INSERT INTO enrollments ...', params);
  await run(db, 'INSERT INTO payments ...', payment);
  await run(db, 'COMMIT');
} catch (err) {
  await run(db, 'ROLLBACK');
  throw err;
}
```

Delete de agregado remove (ou desassocia) os filhos que o domínio não pode abandonar, dentro da mesma transação. Se o contrato antigo respondia texto puro, mantenha o `Content-Type` dessa rota.

## 11. Log sem segredo

Antes:

```javascript
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
```

```python
return jsonify({..., 'secret_key': 'minha-chave-super-secreta-123', 'debug': True})
```

Depois:

```javascript
console.log(`Processando pagamento do usuário ${userId}`);
```

```python
return jsonify({'status': 'ok', 'database': 'connected', 'counts': counts, 'versao': settings.APP_VERSION})
```

PAN, senha, hash e chave não entram em log nem em health check.

## 12. Endpoint perigoso deixa de executar

Antes:

```python
@app.route('/admin/query', methods=['POST'])
def executar_query():
    cursor.execute(request.get_json().get('sql', ''))
```

Depois a rota continua existindo e responde, sem executar SQL de cliente:

```python
def executar_query():
    return jsonify({
        'erro': 'Execução de SQL arbitrário foi desativada por segurança',
        'sucesso': False,
    }), 403
```

Reset administrativo, se permanecer, usa SQL fixo no model (sem string vinda do cliente).
