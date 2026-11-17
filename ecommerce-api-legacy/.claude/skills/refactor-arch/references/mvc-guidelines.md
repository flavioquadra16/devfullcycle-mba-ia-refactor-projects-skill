# Guidelines de arquitetura MVC

O alvo é MVC de API HTTP. View, neste contexto, é a camada de roteamento: ela traduz URL e verbo em chamada de controller. Não é obrigatório existir template HTML.

## Responsabilidades

| Camada | Faz | Não faz |
|---|---|---|
| Model | Schema, consultas parametrizadas, invariantes (estoque, status, hash da senha na gravação) | Ler `request`, devolver `Response`, conhecer status HTTP |
| Controller | Ler entrada, validar contrato HTTP, chamar model/serviço, montar o corpo e o status | Montar SQL por concatenação, guardar segredo, acessar conexão global solta |
| View / Route | Declarar método, caminho e função | Regra de negócio, SQL, serialização de domínio |
| Config | Ler ambiente e `.env.example` | Ser importada por model para decidir regra de negócio, salvo constantes de infra (porta, URI) |
| Middleware | Erro inesperado, CORS, parse do body | Fluxo de um endpoint específico |
| Entry point | Montar as peças e escutar a porta | Regra de um domínio |

Serviço é permitido para efeito colateral (e-mail, cobrança, token). O controller chama o serviço; a rota não.

## Layout por stack

Crie só as pastas que faltam. Mantenha o entry point que o README já usa.

Projeto Python sem pacotes:

```text
app.py
config/settings.py
database.py
models/
controllers/
views/routes.py
middlewares/error_handler.py
services/
.env.example
```

Projeto Node que já usa `src/`:

```text
src/app.js
src/config/settings.js
src/database.js
src/models/
src/controllers/
src/views/routes.js
src/middlewares/errorHandler.js
src/services/
.env.example
```

Projeto que já tem `models/`, `routes/`, `services/`:

- `routes/` permanece como a camada View. Os handlers ficam com uma linha que delega ao controller.
- Crie `controllers/` por domínio.
- Crie `config/settings.py` e `middlewares/error_handler.py`.
- Não mova arquivo de lugar se o ganho for só o nome da pasta.

## Configuração

- Nenhum segredo literal em `.py` ou `.js`.
- Ordem de leitura: variável já exportada no processo, depois `.env`, depois `.env.example` com `setdefault`.
- `.env.example` traz placeholder de laboratório para o boot do desafio (`SECRET_KEY=dev-only-change-me`). Produção sobrescreve pelo ambiente.
- Porta, debug e URI do banco também saem da config.

## Contrato HTTP

Antes de mover uma rota, anote método, caminho, status de sucesso e chaves do JSON. O cliente que já funciona precisa continuar passando no fluxo feliz.

Pode mudar, e deve:

- campo de senha ou segredo que vazava na resposta;
- endpoint de SQL arbitrário, que passa a recusar a execução;
- formato de token falso, trocado por token assinado, desde que a chave `token` continue existindo;
- corpo de erro 500 genérico no lugar de stack ou mensagem interna.

Não mude o nome dos campos de entrada que o cliente envia (`usr`, `eml`, `c_id`, `card`).

## Erros

Middleware devolve JSON (ou o mesmo `text/plain` que a rota já usava, se o contrato daquela rota for texto) com status 500 para exceção não prevista. Erro de validação continua explícito no controller, com a mesma mensagem de antes quando ela faz parte do contrato.

## Validação da Fase 3

1. Subir pela factory ou pelo entry point e garantir que o import não lança.
2. Chamar cada rota original.
3. Executar um fluxo de escrita e a leitura correspondente.
4. Confirmar que segredo e senha não aparecem no JSON de sucesso.
