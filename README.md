# Trion

**Segmento:** HealthTech

**Problema que resolve:** Em unidades de saúde de alta demanda, a triagem clínica manual é um dos principais gargalos operacionais: depende da disponibilidade e da experiência individual de cada profissional, introduz variabilidade subjetiva na classificação de risco e gera tempos de espera imprevisíveis — fatores que, combinados, aumentam o risco de deterioração clínica de pacientes críticos que não são priorizados a tempo. O MediFlow resolve esse problema oferecendo uma API REST cloud-native que aplica um motor de regras clínicas determinístico para calcular, em segundos, o score de risco e o nível de urgência de cada paciente. Por ser Serverless, a solução escala automaticamente conforme a demanda, elimina a necessidade de gerenciamento de infraestrutura e garante padronização completa do protocolo de triagem — independentemente do volume de atendimentos ou da unidade de saúde que a consome.

**Integrantes:**

- Mateus Henrique
- Lucas Buccini
- Marcello Rocha
- Vitor Neves
- João Castro

**Entrega 1:** 06/03

---

## 📋 Sobre o MediFlow

O **MediFlow** é uma API REST de triagem clínica inteligente que classifica o nível de urgência de pacientes com base em um **motor especialista determinístico (White-Box)**. Diferente de abordagens baseadas em Machine Learning, o MVP utiliza exclusivamente regras clínicas bem definidas e auditáveis, garantindo **transparência total** nas decisões de classificação.

**Principais capacidades:**

- Receber dados vitais e sintomas de um paciente via endpoint REST
- Aplicar um conjunto de regras clínicas parametrizáveis para calcular um **score de risco**
- Retornar o nível de urgência classificado (ex.: Emergência, Muito Urgente, Urgente, Pouco Urgente, Não Urgente)
- Registrar cada triagem para consulta e auditoria posterior

## 🏗️ Arquitetura Resumida

O MediFlow segue uma arquitetura **100% Serverless**, eliminando a necessidade de provisionar ou gerenciar servidores.

```
Cliente (HTTP) ──▶ API Gateway ──▶ Function (Lógica de Triagem) ──▶ Banco NoSQL
```

| Camada | Responsabilidade |
|---|---|
| **API Gateway** | Recebe as requisições HTTP, valida headers e roteia para a função |
| **Function (Serverless)** | Executa o motor de regras clínicas e calcula o score de risco |
| **Banco NoSQL** | Persiste os registros de triagem para consulta e auditoria |

> A escolha por Serverless garante **escalabilidade automática**, **custo sob demanda** e **zero gerenciamento de infraestrutura**.

## 🛠️ Tecnologias Utilizadas

| Categoria | Tecnologia |
|---|---|
| Linguagem | `A definir` (Python / Node.js) |
| Provedor Cloud | `A definir` (AWS / GCP / Azure) |
| API Gateway | `A definir` |
| Functions | `A definir` (Lambda / Cloud Functions / Azure Functions) |
| Banco de Dados | `A definir` (DynamoDB / Firestore / CosmosDB) |
| Testes | `A definir` (pytest / Jest) |
| IaC | `A definir` (Serverless Framework / SAM / Terraform) |

## 🚀 Como Executar Localmente

**Pré-requisitos:**

- Runtime da linguagem escolhida instalado (Python 3.x ou Node.js 18+)
- CLI do provedor cloud configurada com credenciais válidas
- Framework de emulação local (ex.: SAM CLI, Serverless Offline)

**Passos:**

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/launchcloud-Trion.git
cd launchcloud-Trion

# 2. Instale as dependências
npm install        # ou pip install -r requirements.txt

# 3. Execute localmente
npm run dev        # ou sam local start-api

# 4. Teste o endpoint de triagem
curl -X POST http://localhost:3000/triage \
  -H "Content-Type: application/json" \
  -d '{"heart_rate": 110, "systolic_bp": 80, "temperature": 39.2, "symptoms": ["chest_pain", "dyspnea"]}'
```

## 📁 Estrutura de Pastas (Clean Architecture)

```
launchcloud-Trion/
├── src/
│   ├── dominio/                  # Núcleo — entidades e regras de negócio
│   │   ├── entidades/            #   Modelos puros (Patient, Triage, RiskFactor)
│   │   └── regras/               #   Motor de regras de pontuação e classificação
│   ├── casos_de_uso/             # Orquestração — casos de uso da triagem
│   ├── infraestrutura/           # Adaptadores externos
│   │   ├── banco_de_dados/       #   Conexão e operações com banco NoSQL
│   │   └── logs/                 #   Logs estruturados em JSON (request_id, LGPD)
│   ├── manipuladores/            # Entry points das funções Serverless (Lambda/CF)
│   └── compartilhado/            # Código compartilhado entre camadas
│       ├── excecoes/             #   Exceções customizadas (ValidationError, etc.)
│       └── esquemas/             #   DTOs e validação de payloads de entrada/saída
├── testes/
│   ├── unitarios/                # Testes unitários do motor de regras
│   └── integracao/               # Testes de integração dos endpoints
├── infra/                        # Templates de infraestrutura como código (IaC)
├── docs/                         # Documentação complementar e diagramas
├── .gitignore
├── PADROES_DE_CODIGO.md
├── README.md
└── package.json                  # ou requirements.txt
```

---

> **Trion** — Triagem inteligente, escalável e auditável. ⚕️
