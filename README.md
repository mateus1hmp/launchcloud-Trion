<p align="center">
  <h1 align="center">Trion</h1>
  <p align="center"><strong>MediFlow API</strong> — Triagem clinica inteligente, escalavel e auditavel</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/segmento-HealthTech-00C9A7?style=for-the-badge" alt="HealthTech" />
  <img src="https://img.shields.io/badge/arquitetura-Serverless-FF6F00?style=for-the-badge" alt="Serverless" />
  <img src="https://img.shields.io/badge/motor-Rule--Based-7C4DFF?style=for-the-badge" alt="Rule-Based" />
  <img src="https://img.shields.io/badge/status-MVP%20em%20desenvolvimento-blue?style=for-the-badge" alt="Status" />
</p>

---

### Problema que resolve

Em unidades de saude de alta demanda, a triagem clinica manual e um dos principais gargalos operacionais: depende da disponibilidade e da experiencia individual de cada profissional, introduz variabilidade subjetiva na classificacao de risco e gera tempos de espera imprevisiveis — fatores que, combinados, aumentam o risco de deterioracao clinica de pacientes criticos que nao sao priorizados a tempo. O **MediFlow** resolve esse problema oferecendo uma API REST cloud-native que aplica um motor de regras clinicas deterministico para calcular, em segundos, o score de risco e o nivel de urgencia de cada paciente. Por ser Serverless, a solucao escala automaticamente conforme a demanda, elimina a necessidade de gerenciamento de infraestrutura e garante padronizacao completa do protocolo de triagem.

### Integrantes

| Nome | GitHub |
|------|--------|
| Mateus Henrique | `@mateus1hmp` |
| Lucas Buccini | `@lucasbuccini` |
| Marcello Rocha | `@marcellorocha` |
| Vitor Neves | `@vitorneves` |
| Joao Castro | `@joaocastro` |

> **Entrega 1:** 06/03

---

## Sobre o MediFlow

O **MediFlow** e uma API REST de triagem clinica inteligente que classifica o nivel de urgencia de pacientes com base em um **motor especialista deterministico (White-Box)**. Diferente de abordagens baseadas em Machine Learning, o MVP utiliza exclusivamente regras clinicas bem definidas e auditaveis, garantindo **transparencia total** nas decisoes de classificacao.

**Principais capacidades:**

- Receber dados vitais e sintomas de um paciente via endpoint REST
- Aplicar um conjunto de regras clinicas parametrizaveis para calcular um **score de risco**
- Retornar o nivel de urgencia classificado (`LOW` | `MEDIUM` | `HIGH` | `CRITICAL`)
- Registrar cada triagem para consulta e auditoria posterior

---

## Arquitetura

O MediFlow segue uma arquitetura **100% Serverless**, eliminando a necessidade de provisionar ou gerenciar servidores.

```
Cliente (HTTP) ──▶ API Gateway ──▶ Function (Logica de Triagem) ──▶ Banco NoSQL
```

| Camada | Responsabilidade |
|--------|-----------------|
| **API Gateway** | Recebe requisicoes HTTP, aplica rate limiting, valida API keys e roteia endpoints |
| **Serverless Function** | Executa o motor de regras, calcula scores e monta a resposta |
| **Banco NoSQL** | Armazena documentos de triagem com chaveamento por paciente e timestamp |

> Escalabilidade automatica, custo sob demanda e zero gerenciamento de infraestrutura.

---

## Tecnologias

| Categoria | Tecnologia |
|-----------|-----------|
| Linguagem | `A definir` (Python / Node.js) |
| Provedor Cloud | `A definir` (AWS / GCP / Azure) |
| API Gateway | `A definir` |
| Functions | `A definir` (Lambda / Cloud Functions / Azure Functions) |
| Banco de Dados | `A definir` (DynamoDB / Firestore / CosmosDB) |
| Testes | `A definir` (pytest / Jest) |
| IaC | `A definir` (Serverless Framework / SAM / Terraform) |

---

## Como Executar Localmente

**Pre-requisitos:**

- Runtime da linguagem escolhida instalado (Python 3.x ou Node.js 18+)
- CLI do provedor cloud configurada com credenciais validas
- Framework de emulacao local (ex.: SAM CLI, Serverless Offline)

**Passos:**

```bash
# 1. Clone o repositorio
git clone https://github.com/mateus1hmp/launchcloud-Trion.git
cd launchcloud-Trion

# 2. Instale as dependencias
npm install        # ou pip install -r requirements.txt

# 3. Execute localmente
npm run dev        # ou sam local start-api

# 4. Teste o endpoint de triagem
curl -X POST http://localhost:3000/triage \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "PAT-001", "age": 67, "symptoms": {"chest_pain": true}, "vitals": {"heart_rate": 120}}'
```

---

## Estrutura de Pastas

```
launchcloud-Trion/
├── src/
│   ├── dominio/                  # Nucleo — entidades e regras de negocio
│   │   ├── entidades/            #   Modelos puros (Patient, Triage, RiskFactor)
│   │   └── regras/               #   Motor de regras de pontuacao e classificacao
│   ├── casos_de_uso/             # Orquestracao — casos de uso da triagem
│   ├── infraestrutura/           # Adaptadores externos
│   │   ├── banco_de_dados/       #   Conexao e operacoes com banco NoSQL
│   │   └── logs/                 #   Logs estruturados em JSON (request_id, LGPD)
│   ├── manipuladores/            # Entry points das funcoes Serverless
│   └── compartilhado/            # Codigo compartilhado entre camadas
│       ├── excecoes/             #   Excecoes customizadas (ValidationError, etc.)
│       └── esquemas/             #   DTOs e validacao de payloads de entrada/saida
├── testes/
│   ├── unitarios/                # Testes unitarios do motor de regras
│   └── integracao/               # Testes de integracao dos endpoints
├── infra/                        # Templates de infraestrutura como codigo (IaC)
├── docs/                         # Documentacao complementar e diagramas
├── .gitignore
├── PADROES_DE_CODIGO.md
├── README.md
└── package.json                  # ou requirements.txt
```

---

## Padrao de Commits

Este projeto segue **Conventional Commits**. Todo commit usa o formato:

```
<tipo>: <descricao curta em ingles>
```

| Tipo | Quando usar | Exemplo |
|------|------------|---------|
| `feat` | Nova funcionalidade | `feat: add risk score calculation` |
| `fix` | Correcao de bug | `fix: handle missing patient_id` |
| `docs` | Apenas documentacao | `docs: update README with setup steps` |
| `refactor` | Refatoracao sem mudar comportamento | `refactor: extract score rules to module` |
| `test` | Adicionar ou corrigir testes | `test: add unit tests for triage engine` |
| `chore` | Manutencao (configs, deps, CI) | `chore: add serverless framework config` |
| `style` | Formatacao (sem mudanca de logica) | `style: fix indentation in handler` |

> Consulte o [`PADROES_DE_CODIGO.md`](PADROES_DE_CODIGO.md) para ver todas as regras do projeto.

---

<p align="center">
  <strong>Trion</strong> — Triagem inteligente, escalavel e auditavel.
</p>
