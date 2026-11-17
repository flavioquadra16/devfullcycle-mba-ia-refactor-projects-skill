# Análise de projeto

Use estas heurísticas na Fase 1. A primeira evidência forte vence; confirme com uma segunda fonte antes de cravar framework ou banco.

## Linguagem

| Evidência | Linguagem |
|---|---|
| `requirements.txt`, `pyproject.toml`, `*.py` | Python |
| `package.json` com `dependencies`, `*.js` | JavaScript (Node.js) |
| `go.mod`, `*.go` | Go |
| `pom.xml` ou `build.gradle`, `*.java` | Java |
| `*.csproj`, `Program.cs` | C# |
| `composer.json`, `*.php` | PHP |
| `Gemfile`, `*.rb` | Ruby |

Versão: campo `python` / `engines` / toolchain, ou a versão pinada da dependência principal. Se não houver versão, omita o número e registre o framework.

## Framework

Procure o import ou a dependência, não o nome da pasta.

| Sinal | Framework |
|---|---|
| `flask` em `requirements.txt` ou `from flask import` | Flask |
| `express` em `package.json` ou `require('express')` | Express |
| `django`, `fastapi`, `@nestjs/core`, `spring-boot`, `gin` | o framework correspondente |
| nenhum framework, só `http` / `socket` | biblioteca padrão HTTP |

Dependências diretas: liste as de runtime do manifesto, sem as transitivas do lockfile.

## Banco de dados

| Sinal | Banco |
|---|---|
| `sqlite3`, `better-sqlite3`, arquivo `*.db`, URI `sqlite:` | SQLite |
| `psycopg`, `pg`, `postgres://` | PostgreSQL |
| `mysql2`, `pymysql` | MySQL |
| `mongodb`, `mongoose` | MongoDB |
| `SQLAlchemy`, `sequelize`, `prisma`, `typeorm` | o ORM, mais o dialeto da URI |

Tabelas: leia `CREATE TABLE`, modelos (`__tablename__`, `sequelize.define`) e migrations. Se o schema for criado em runtime, vale assim mesmo.

## Domínio

Infira o domínio pelos substantivos das rotas, tabelas e modelos (`produtos`, `orders`, `tasks`, `courses`). Escreva uma linha: tipo de sistema + entidades principais. Exemplo: `E-commerce API (produtos, pedidos, usuários)`.

## Arquitetura atual

Classifique pelo que os arquivos fazem, não pelo nome da pasta.

- **Monólito sem camadas:** regras, SQL e rotas concentrados em poucos arquivos.
- **Parcial:** existem `models/`, `routes/` ou `services/`, mas rota ainda valida, consulta e serializa, ou não há controller.
- **MVC reconhecível:** rota só encaminha, controller orquestra, model acessa dados, config fica fora do código de negócio.

Conte os arquivos de código analisados (fonte da aplicação). Não conte skill, relatório, banco, `node_modules` ou virtualenv.

## Saída

Preencha o bloco da Fase 1 definido em `SKILL.md`. Não proponha correção nesta fase.
