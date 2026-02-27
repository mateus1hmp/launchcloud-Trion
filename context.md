# MediFlow API — Technical Knowledge Base

> **Startup:** Trion
> **Documento:** Especificacao tecnica para agentes de IA (Knowledge Base)
> **Versao:** 1.0.0
> **Tipo:** API REST — MVP Deterministico (sem Machine Learning)

---

## 1. Visao Geral e MVP

### Objetivo

A MediFlow e uma API de triagem medica automatizada que calcula scores de risco para pacientes com base em sintomas, sinais vitais e historico clinico. O sistema auxilia profissionais de saude na priorizacao de atendimentos.

### Principios do MVP

- **Sem Machine Learning:** o MVP utiliza exclusivamente um motor de regras deterministico (White-Box). Nenhum modelo estatistico ou de aprendizado de maquina e empregado.
- **Explicabilidade total:** cada ponto do score final e rastreavel a uma regra explicita. O sistema deve sempre retornar quais fatores contribuiram para a pontuacao.
- **API REST Stateless:** nenhuma sessao ou estado e mantido entre requisicoes. Toda informacao necessaria deve estar contida no payload de entrada.
- **Serverless:** a aplicacao roda inteiramente em funcoes serverless, sem servidores gerenciados manualmente.
- **Resiliencia a dados parciais:** campos ausentes no payload de entrada nao devem causar erro. O motor de regras simplesmente ignora fatores cujos dados nao foram fornecidos.

---

## 2. Arquitetura Cloud

### Fluxo de Requisicao

```
Cliente (HTTP)
    |
    v
API Gateway (roteamento, throttling, autenticacao)
    |
    v
Serverless Function (logica de triagem)
    |
    v
Banco NoSQL (persistencia de documentos)
```

### Componentes

| Componente          | Responsabilidade                                                                 |
|---------------------|----------------------------------------------------------------------------------|
| **API Gateway**     | Recebe requisicoes HTTP, aplica rate limiting, valida API keys, roteia endpoints  |
| **Serverless Function** | Executa o motor de regras, calcula scores, monta resposta, persiste resultado |
| **Banco NoSQL**     | Armazena documentos de triagem com chaveamento por paciente e timestamp           |

### Requisitos Transversais

- **Logs estruturados:** todas as funcoes devem emitir logs em formato JSON com campos padronizados (`timestamp`, `request_id`, `patient_id_hash`, `action`, `duration_ms`).
- **Anonimizacao (LGPD):** dados pessoais identificaveis (nome, CPF, endereco) **nao** sao armazenados. O `patient_id` e tratado como identificador pseudonimizado. Logs nunca devem conter dados clinicos em texto claro — apenas hashes ou referencias opacas.
- **Correlacao de requisicoes:** cada requisicao recebe um `request_id` unico (UUID v4) propagado em todos os logs e respostas.

---

## 3. Motor de Triagem (Regras de Negocio)

### Sistema de Pontuacao

O motor e puramente aditivo. Cada fator de risco identificado no payload soma pontos ao score total. Fatores ausentes contribuem com **0 pontos**.

#### Tabela de Pontuacao

| Fator                         | Condicao               | Pontos |
|-------------------------------|------------------------|--------|
| Dor no peito                  | `chest_pain == true`   | +40    |
| Falta de ar                   | `shortness_of_breath == true` | +30 |
| Frequencia cardiaca elevada   | `heart_rate > 110`     | +20    |
| Idade avancada                | `age > 60`             | +15    |
| Pressao sistolica elevada     | `systolic_bp > 140`    | +10    |
| Diabetes                      | `diabetes == true`     | +10    |
| Febre                         | `temperature > 38`     | +10    |

#### Classificacao de Urgencia

| Faixa de Score | Nivel        | `urgency_level` |
|----------------|--------------|------------------|
| 0 — 29         | Baixo        | `LOW`            |
| 30 — 59        | Medio        | `MEDIUM`         |
| 60 — 89        | Alto         | `HIGH`           |
| 90+            | Critico      | `CRITICAL`       |

### Regras Complementares

- `needs_immediate_attention`: `true` se `urgency_level` for `CRITICAL` **ou** se `chest_pain == true` e `shortness_of_breath == true` simultaneamente.
- `recommended_specialty`: mapeamento baseado nos sintomas predominantes:
  - Dor no peito ou frequencia cardiaca elevada → `"cardiology"`
  - Falta de ar sem dor no peito → `"pulmonology"`
  - Febre isolada → `"general_practice"`
  - Demais combinacoes → `"emergency"`
- `confidence_level`: no MVP deterministico, o valor e fixo em `"deterministic"` para indicar que o resultado vem de regras, nao de modelo probabilistico.

---

## 4. Schema de Dados (Payloads)

### 4.1 JSON de Entrada — POST /triage

```json
{
  "patient_id": "PAT-2024-001",
  "age": 67,
  "gender": "M",
  "symptoms": {
    "chest_pain": true,
    "shortness_of_breath": true,
    "dizziness": false,
    "nausea": false
  },
  "vitals": {
    "heart_rate": 120,
    "systolic_bp": 145,
    "diastolic_bp": 95,
    "temperature": 37.2,
    "oxygen_saturation": 94
  },
  "chronic_diseases": {
    "diabetes": true,
    "hypertension": true,
    "asthma": false
  },
  "clinical_notes": "Paciente relata dor no peito ha 2 horas com irradiacao para braco esquerdo."
}
```

#### Campos e Regras de Validacao

| Campo               | Tipo     | Obrigatorio | Notas                                                        |
|---------------------|----------|-------------|--------------------------------------------------------------|
| `patient_id`        | string   | Sim         | Identificador unico pseudonimizado                           |
| `age`               | integer  | Nao         | Se ausente, regra de idade nao pontua                        |
| `gender`            | string   | Nao         | Valores aceitos: `"M"`, `"F"`, `"OTHER"`                     |
| `symptoms`          | object   | Nao         | Cada campo booleano; se objeto ausente, nenhum sintoma pontua |
| `vitals`            | object   | Nao         | Cada campo numerico; se objeto ausente, nenhum vital pontua   |
| `chronic_diseases`  | object   | Nao         | Cada campo booleano; se objeto ausente, nenhuma doenca pontua |
| `clinical_notes`    | string   | Nao         | Texto livre; armazenado mas nao processado no MVP             |

**Tratamento de campos ausentes:** o motor de regras deve usar acesso seguro (ex: `dict.get()` / optional chaining) para cada campo. Um payload contendo apenas `{ "patient_id": "X" }` deve ser processado normalmente, resultando em score 0 e urgencia `LOW`.

### 4.2 JSON de Saida — Resposta do POST /triage

```json
{
  "triage_id": "TRG-20240115-abc123",
  "patient_id": "PAT-2024-001",
  "timestamp": "2024-01-15T14:30:00Z",
  "urgency_level": "CRITICAL",
  "risk_score": 125,
  "recommended_specialty": "cardiology",
  "needs_immediate_attention": true,
  "confidence_level": "deterministic",
  "risk_factors": [
    { "factor": "chest_pain", "points": 40, "description": "Dor no peito reportada" },
    { "factor": "shortness_of_breath", "points": 30, "description": "Falta de ar reportada" },
    { "factor": "heart_rate", "points": 20, "description": "Frequencia cardiaca acima de 110 (valor: 120)" },
    { "factor": "age", "points": 15, "description": "Idade acima de 60 (valor: 67)" },
    { "factor": "systolic_bp", "points": 10, "description": "Pressao sistolica acima de 140 (valor: 145)" },
    { "factor": "diabetes", "points": 10, "description": "Diabetes registrada" }
  ]
}
```

#### Campos da Resposta

| Campo                       | Tipo     | Descricao                                                             |
|-----------------------------|----------|-----------------------------------------------------------------------|
| `triage_id`                 | string   | Identificador unico da triagem (gerado pelo sistema)                  |
| `patient_id`                | string   | Eco do identificador do paciente recebido                             |
| `timestamp`                 | string   | Data/hora UTC no formato ISO 8601                                     |
| `urgency_level`             | string   | `LOW` \| `MEDIUM` \| `HIGH` \| `CRITICAL`                            |
| `risk_score`                | integer  | Soma total dos pontos de risco                                        |
| `recommended_specialty`     | string   | Especialidade medica recomendada                                      |
| `needs_immediate_attention` | boolean  | Flag de atencao imediata                                              |
| `confidence_level`          | string   | Sempre `"deterministic"` no MVP                                       |
| `risk_factors`              | array    | Lista detalhada de cada fator que contribuiu para o score             |

---

## 5. Design de Banco de Dados NoSQL

### Estrategia de Chaveamento

| Chave            | Campo         | Justificativa                                                        |
|------------------|---------------|----------------------------------------------------------------------|
| **Partition Key** | `patient_id` | Agrupa todas as triagens de um paciente na mesma particao             |
| **Sort Key**      | `timestamp`  | Ordena triagens cronologicamente, permite queries por intervalo       |

### Estrutura do Documento

```json
{
  "patient_id": "PAT-2024-001",
  "timestamp": "2024-01-15T14:30:00Z",
  "triage_id": "TRG-20240115-abc123",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "input": {
    "age": 67,
    "gender": "M",
    "symptoms": {
      "chest_pain": true,
      "shortness_of_breath": true,
      "dizziness": false,
      "nausea": false
    },
    "vitals": {
      "heart_rate": 120,
      "systolic_bp": 145,
      "diastolic_bp": 95,
      "temperature": 37.2,
      "oxygen_saturation": 94
    },
    "chronic_diseases": {
      "diabetes": true,
      "hypertension": true,
      "asthma": false
    },
    "clinical_notes": "Paciente relata dor no peito ha 2 horas com irradiacao para braco esquerdo."
  },
  "output": {
    "urgency_level": "CRITICAL",
    "risk_score": 125,
    "recommended_specialty": "cardiology",
    "needs_immediate_attention": true,
    "confidence_level": "deterministic",
    "risk_factors": [
      { "factor": "chest_pain", "points": 40, "description": "Dor no peito reportada" },
      { "factor": "shortness_of_breath", "points": 30, "description": "Falta de ar reportada" },
      { "factor": "heart_rate", "points": 20, "description": "Frequencia cardiaca acima de 110 (valor: 120)" },
      { "factor": "age", "points": 15, "description": "Idade acima de 60 (valor: 67)" },
      { "factor": "systolic_bp", "points": 10, "description": "Pressao sistolica acima de 140 (valor: 145)" },
      { "factor": "diabetes", "points": 10, "description": "Diabetes registrada" }
    ]
  },
  "metadata": {
    "api_version": "1.0.0",
    "engine": "rule-based-v1",
    "processing_time_ms": 45
  }
}
```

### Indices e Queries Esperadas

| Query                                  | Uso das Chaves                                          |
|----------------------------------------|---------------------------------------------------------|
| Todas as triagens de um paciente       | `PK = patient_id`                                       |
| Triagem mais recente de um paciente    | `PK = patient_id`, `SK` desc, `LIMIT 1`                |
| Triagens em um intervalo de datas      | `PK = patient_id`, `SK BETWEEN timestamp_a AND timestamp_b` |

---

## 6. Endpoints Principais

### POST /triage

Recebe dados do paciente e retorna o resultado da triagem.

| Atributo        | Valor                              |
|-----------------|------------------------------------|
| **Metodo**      | `POST`                             |
| **Path**        | `/triage`                          |
| **Content-Type**| `application/json`                 |
| **Request Body**| Schema de entrada (secao 4.1)      |
| **Response 200**| Schema de saida (secao 4.2)        |
| **Response 400**| `{ "error": "patient_id is required" }` |
| **Response 500**| `{ "error": "internal server error", "request_id": "..." }` |

### GET /triage/{patient_id}

Retorna o historico de triagens de um paciente.

| Atributo        | Valor                              |
|-----------------|------------------------------------|
| **Metodo**      | `GET`                              |
| **Path**        | `/triage/{patient_id}`             |
| **Path Param**  | `patient_id` (string, obrigatorio) |
| **Query Params**| `limit` (int, opcional, default 10), `start_date` (ISO 8601, opcional), `end_date` (ISO 8601, opcional) |
| **Response 200**| `{ "patient_id": "...", "triages": [ ... ] }` |
| **Response 404**| `{ "error": "patient not found" }` |

### GET /health

Health check do servico.

| Atributo        | Valor                              |
|-----------------|------------------------------------|
| **Metodo**      | `GET`                              |
| **Path**        | `/health`                          |
| **Response 200**| Ver exemplo abaixo                 |

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "engine": "rule-based-v1",
  "timestamp": "2024-01-15T14:30:00Z"
}
```

---

## 7. Codigos de Erro Padronizados

| HTTP Status | Codigo              | Descricao                          |
|-------------|---------------------|------------------------------------|
| 400         | `VALIDATION_ERROR`  | Payload invalido ou campo obrigatorio ausente |
| 404         | `NOT_FOUND`         | Paciente ou triagem nao encontrado |
| 429         | `RATE_LIMITED`      | Limite de requisicoes excedido     |
| 500         | `INTERNAL_ERROR`    | Erro interno do servidor           |

Formato padrao de erro:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "patient_id is required",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

---

## 8. Decisoes Tecnicas para Implementacao

- **Linguagem:** a definir (Python e a escolha recomendada para o ecossistema serverless).
- **Formato de IDs:** `triage_id` segue o padrao `TRG-{YYYYMMDD}-{random_hex_6}`.
- **Timezone:** todos os timestamps em UTC (ISO 8601 com sufixo `Z`).
- **Versionamento:** a API deve incluir o header `X-API-Version: 1.0.0` em todas as respostas.
- **Idempotencia:** o endpoint POST /triage nao e idempotente — cada chamada gera uma nova triagem.
- **Tamanho maximo do payload:** 64 KB.
- **TTL de dados:** definir politica de retencao conforme LGPD (sugestao: 5 anos para dados de saude).
