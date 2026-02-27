# Diretrizes de Clean Code — MediFlow API

> Regras inegociaveis para todo codigo commitado no repositorio.
> Aplica-se a: Mateus, Lucas, Marcello, Vitor e Joao.

---

## 1. Nomenclatura Explicita

- Nomes de variaveis, funcoes e arquivos devem ser **autoexplicativos**. Nao use abreviacoes ambiguas.
- Prefira `calculate_risk_score` em vez de `calc_rs`. Prefira `patient_age` em vez de `pAge`.
- Nomes de constantes em `UPPER_SNAKE_CASE`. Nomes de funcoes e variaveis em `snake_case` (Python) ou `camelCase` (Node.js).
- Se voce precisa de um comentario para explicar **o que** uma variavel armazena, o nome dela esta ruim.

```
# Ruim
def calc(d):
    s = d.get("hr", 0)
    ...

# Bom
def calculate_risk_score(patient_data):
    heart_rate = patient_data.get("heart_rate", 0)
    ...
```

---

## 2. Funcoes Puras e Responsabilidade Unica (SOLID)

- Cada funcao faz **uma coisa**. Se voce usa "e" para descrever o que ela faz, quebre em duas.
- O motor de regras **nao** acessa banco de dados. O handler **nao** calcula score. Respeite as camadas.
- Funcoes do `dominio/` devem ser **puras**: mesma entrada, mesma saida, sem efeitos colaterais.
- Limite de **30 linhas** por funcao como referencia. Se ultrapassar, revise a responsabilidade.

```
# Ruim — faz triagem E salva no banco
def handle_triage(data):
    score = sum(...)
    db.save(score)
    return score

# Bom — cada camada faz o seu papel
# dominio/regras/
def calculate_risk_score(patient_data): ...

# casos_de_uso/
def execute_triage(patient_data, repository): ...

# manipuladores/
def triage_handler(event): ...
```

---

## 3. Tratamento de Erros Explicito

- **Nunca** engula excecoes silenciosamente (`except: pass` / `catch {}`).
- Toda excecao deve ser logada com `request_id` para rastreabilidade.
- Use excecoes customizadas para erros de dominio (`ValidationError`, `PatientNotFoundError`).
- Erros inesperados retornam `500` com `request_id` — **nunca** exponha stack traces ao cliente.

```
# Ruim
try:
    process(data)
except:
    pass

# Bom
try:
    process(data)
except ValidationError as e:
    logger.warning({"request_id": req_id, "error": str(e)})
    return {"statusCode": 400, "body": {"error": {"code": "VALIDATION_ERROR", "message": str(e)}}}
except Exception as e:
    logger.error({"request_id": req_id, "error": str(e)})
    return {"statusCode": 500, "body": {"error": {"code": "INTERNAL_ERROR", "request_id": req_id}}}
```

---

## 4. Retornos de API Padronizados

- Toda resposta segue o schema definido no `context.md` — sem campos inventados.
- Respostas de sucesso: HTTP `200` com o body documentado.
- Respostas de erro: **sempre** no formato `{ "error": { "code": "...", "message": "...", "request_id": "..." } }`.
- O header `X-API-Version` deve estar presente em **todas** as respostas.
- Nunca retorne `200` para operacoes que falharam.

---

## 5. Commits e Organizacao

- Commits em ingles, no imperativo: `Add risk score calculation`, nao `added stuff`.
- Um commit = uma mudanca logica. Nao misture refatoracao com feature nova.
- Todo codigo deve passar nos testes **antes** de ser enviado ao branch principal.
- Pull Requests exigem revisao de pelo menos **1 outro membro** do time.
