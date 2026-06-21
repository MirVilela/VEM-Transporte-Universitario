# 📊 SCHEMA.md: Constituição dos Dados e Contratos de API

## 📑 1. Identificação do Modelo

**Projeto:** Sistema Preditivo de Transporte Universitário (SPTU) — Offline-First  
**Arquiteta de Dados:** Ana (Backend)  
**Revisora:** Maria (Conformidade/LGPD)  
**Versão:** 2.0  

---

## 🏛️ 2. Entidades e Atributos (The Law)

*Esta tabela define os campos que serão persistidos no banco de dados SQLite local. Nenhuma implementação pode adicionar campos "enfeite" fora desta lista.*

> ⚠️ **RS02 — Proibição de Auto-Incremento:** O uso de chaves primárias (PK) auto-incrementais está explicitamente proibido. O CPF do aluno atua como chave primária imutável. IDs compostos são utilizados nas demais tabelas.

### 👤 Tabela: `alunos`

*Cadastro importado via planilha da empresa prestadora de serviço.*

| Campo | Tipo | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `cpf` | TEXT | **Primary Key** | CPF do aluno (somente dígitos, 11 caracteres). Chave imutável conforme RS02. |
| `nome` | TEXT | Not Null | Nome completo do aluno. |
| `pin` | TEXT | Not Null | PIN de 4 dígitos para autenticação (armazenado como hash). |
| `rota` | TEXT | Not Null | Rota do aluno (ex: "Cidade A → Campus"). |
| `tipo_vaga` | TEXT | Default: 'NORMAL' | Tipo de vaga: 'NORMAL' ou 'EXCECAO' (vaga blindada para alunos de locais distantes). |
| `ativo` | INTEGER | Default: 1 | Status do aluno: 1=ativo, 0=inativo. |

### 📅 Tabela: `reservas`

*Intenção de viagem semanal registrada pelo aluno via PWA.*

| Campo | Tipo | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | **Primary Key** | ID manual composto: `{cpf}_{data}` (ex: "12345678901_2026-06-10"). |
| `cpf` | TEXT | FK → alunos | CPF do aluno que fez a reserva. |
| `data` | TEXT | Not Null | Data da viagem (formato: YYYY-MM-DD). |
| `ida` | INTEGER | Default: 0 | Intenção de ida: 1=vai, 0=não vai. |
| `volta` | INTEGER | Default: 0 | Intenção de volta: 1=volta, 0=não volta. |
| `status` | TEXT | Default: 'ATIVA' | Estado da reserva: 'ATIVA', 'CANCELADA' ou 'BLOQUEADA'. |
| `criado_em` | TEXT | Default: NOW | Timestamp ISO 8601 do momento da criação. |

### 🚌 Tabela: `veiculos`

*Frota disponível cadastrada pela gestora.*

| Campo | Tipo | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | **Primary Key** | Código manual do veículo (ex: "ONIBUS-01", "VAN-03"). |
| `tipo` | TEXT | Not Null | Categoria: 'ONIBUS', 'MICRO' ou 'VAN'. |
| `capacidade` | INTEGER | Not Null | Número total de assentos disponíveis. |
| `ativo` | INTEGER | Default: 1 | Status do veículo: 1=ativo, 0=inativo. |

### ✅ Tabela: `checkins`

*Registro de embarque físico validado pelo motorista.*

| Campo | Tipo | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | **Primary Key** | ID manual composto: `{cpf}_{veiculo_id}_{data}_{tipo}` |
| `cpf` | TEXT | FK → alunos | CPF do aluno embarcado. |
| `veiculo_id` | TEXT | FK → veiculos | Código do veículo utilizado. |
| `data` | TEXT | Not Null | Data do embarque (formato: YYYY-MM-DD). |
| `tipo` | TEXT | Not Null | Trecho do embarque: 'IDA' ou 'VOLTA'. |
| `confirmado_em` | TEXT | Default: NOW | Timestamp ISO 8601 da confirmação física. |

### 📢 Tabela: `avisos`

*Mural de avisos para comunicados aos alunos (Requisito A).*

| Campo | Tipo | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | **Primary Key** | ID único gerado. |
| `titulo` | TEXT | Not Null | Título do aviso. |
| `mensagem` | TEXT | Not Null | Conteúdo do aviso. |
| `tipo` | TEXT | Default: 'INFO' | Tipo do aviso: 'INFO' ou 'URGENTE'. |
| `criado_em` | TEXT | Default: NOW | Timestamp de criação. |
| `expira_em` | TEXT | Nullable | Data de expiração (opcional, YYYY-MM-DD). |
| `ativo` | INTEGER | Default: 1 | 1=ativo (visível), 0=arquivado. |

### 🛣️ Tabela: `rotas`

*Cadastro das rotas disponíveis para viagens (Escalabilidade).*

| Campo | Tipo | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | **Primary Key** | ID único (slug gerado, ex: "ROTA-CIDADEA"). |
| `nome` | TEXT | Not Null | Nome descritivo da rota (ex: "Cidade A -> Campus"). |
| `ativo` | INTEGER | Default: 1 | Status da rota (1=ativa, 0=inativa). |

### 📍 Tabela: `pontos_rota`

*Pontos pré-cadastrados para controle de viagem.*

| Campo | Tipo | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | **Primary Key** | ID único (slug da rota + ordem). |
| `rota_id` | TEXT | FK → rotas | ID da rota à qual o ponto pertence. |
| `nome` | TEXT | Not Null | Nome descritivo do ponto (ex: "Rodoviária"). |
| `ordem` | INTEGER | Not Null | Ordem cronológica na rota (1, 2, 3...). |

### 🚌 Tabela: `status_viagem`

*Rastreamento das viagens do dia (Requisito B).*

| Campo | Tipo | Restrição | Descrição |
| :--- | :--- | :--- | :--- |
| `id` | TEXT | **Primary Key** | ID composto: `{veiculo_id}_{data}_{tipo}`. |
| `veiculo_id` | TEXT | FK → veiculos | ID do veículo. |
| `data` | TEXT | Not Null | Data da viagem (YYYY-MM-DD). |
| `tipo` | TEXT | Not Null | Tipo de trajeto ('IDA' ou 'VOLTA'). |
| `ponto_atual_id`| TEXT | Nullable | Ponto onde o veículo se encontra no momento. |
| `status` | TEXT | Default: 'AGUARDANDO' | Status da viagem ('AGUARDANDO', 'EM_ROTA', 'FINALIZADA'). |
| `atualizado_em` | TEXT | Default: NOW | Timestamp da última atualização de localização. |

---

## 📜 3. Contrato de API (JSON is Law)

*Este é o formato exato que as requisições e respostas devem seguir para garantir o funcionamento Offline-First.*

### 🔐 Autenticação (POST /api/login)

**Entrada:**
```json
{
  "cpf": "12345678901",
  "pin": "1234"
}
```

**Saída (Sucesso):**
```json
{
  "sucesso": true,
  "aluno": {
    "cpf": "12345678901",
    "nome": "João Silva",
    "rota": "Cidade A → Campus",
    "tipo_vaga": "NORMAL"
  }
}
```

### 📅 Registrar Reserva Semanal (POST /api/reservar)

**Entrada:**
```json
{
  "cpf": "12345678901",
  "reservas": [
    { "data": "2026-06-10", "ida": 1, "volta": 1 },
    { "data": "2026-06-11", "ida": 1, "volta": 0 },
    { "data": "2026-06-12", "ida": 0, "volta": 0 }
  ]
}
```

**Saída (Sucesso):**
```json
{
  "sucesso": true,
  "mensagem": "Reservas da semana registradas com sucesso.",
  "total_registradas": 2
}
```

### 📊 Consultar Semana do Aluno (GET /api/semana?cpf={cpf})

**Saída:**
```json
{
  "semana": [
    { "data": "2026-06-10", "dia": "Segunda", "ida": 1, "volta": 1, "status": "ATIVA" },
    { "data": "2026-06-11", "dia": "Terça", "ida": 1, "volta": 0, "status": "ATIVA" }
  ]
}
```

### 📈 Painel da Gestora (GET /api/painel)

*Requer Header `X-Admin-Token`.*

**Saída:**
```json
{
  "resumo_diario": [
    {
      "data": "2026-06-10",
      "dia": "Segunda",
      "total_ida": 85,
      "total_volta": 72,
      "excecoes_ida": 5,
      "excecoes_volta": 4,
      "sugestao_frota": {
        "ida": [{ "tipo": "ONIBUS", "qtd": 2 }],
        "volta": [{ "tipo": "ONIBUS", "qtd": 1 }, { "tipo": "MICRO", "qtd": 1 }]
      }
    }
  ]
}
```

### 📋 Checklist do Motorista (GET /api/checklist/{data}?tipo={IDA|VOLTA})

*Requer Header `X-Admin-Token`.*

**Saída:**
```json
{
  "data": "2026-06-10",
  "tipo": "VOLTA",
  "passageiros": [
    { "cpf": "12345678901", "nome": "João Silva", "tipo_vaga": "NORMAL", "checkin": false },
    { "cpf": "98765432100", "nome": "Maria Souza", "tipo_vaga": "EXCECAO", "checkin": false }
  ]
}
```

### ✅ Confirmar Embarque (POST /api/checkin)

**Entrada:**
```json
{
  "cpf": "12345678901",
  "veiculo_id": "ONIBUS-01",
  "data": "2026-06-10",
  "tipo": "VOLTA"
}
```

**Saída:**
```json
{
  "sucesso": true,
  "vagas_restantes": 18,
  "capacidade_total": 44
}
```

### 🚌 Listar Veículos (GET /api/veiculos)

*Requer Header `X-Admin-Token`.*

**Saída:**
```json
[
  { "id": "ONIBUS-01", "tipo": "ONIBUS", "capacidade": 44, "ativo": 1 },
  { "id": "VAN-01", "tipo": "VAN", "capacidade": 15, "ativo": 1 }
]
```

### 📢 Listar Avisos Ativos (GET /api/avisos)

*Público / WhatsApp-ready.*

**Saída:**
```json
{
  "total": 1,
  "avisos": [
    {
      "id": "AV-1623948392",
      "titulo": "Rua X interditada",
      "mensagem": "Embarque será feito na rua Y.",
      "tipo": "URGENTE",
      "criado_em": "2026-06-10 10:00:00",
      "expira_em": "2026-06-11",
      "ativo": 1
    }
  ]
}
```

### 🛣️ Listar Rotas (GET /api/rotas)

*Requer Header `X-Admin-Token`.*

**Saída:**
```json
{
  "rotas": [
    { "id": "ROTA-CIDADEA", "nome": "Cidade A -> Campus", "ativo": 1 }
  ]
}
```

### 📍 Listar Pontos de Rota (GET /api/pontos-rota)

*Requer Header `X-Admin-Token`.*

**Saída:**
```json
{
  "pontos": [
    { "id": "PR-CIDADEA-1", "rota_id": "ROTA-CIDADEA", "rota_nome": "Cidade A -> Campus", "nome": "Saida Garagem", "ordem": 1 }
  ]
}
```

### 📍 Editar Ponto de Rota (PUT /api/pontos-rota/{id})

*Requer Header `X-Admin-Token`.*

**Entrada:**
```json
{
  "nome": "Terminal Central",
  "ordem": 2
}
```

### 📊 Relatório de Viagens (GET /api/relatorios/viagens)

*Requer Header `X-Admin-Token`.*
Parâmetros de query: `?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD`

**Saída:** Arquivo texto/csv via stream.

### 🚌 Atualizar Status de Viagem (PUT /api/status-viagem)

*Requer Header `X-Admin-Token`.*

**Entrada:**
```json
{
  "veiculo_id": "ONIBUS-01",
  "data": "2026-06-10",
  "tipo": "IDA",
  "ponto_id": "PR-CIDADEA-1"
}
```

### 🗺️ Consultar Status Diário (GET /api/status-viagem/{data}?tipo={IDA|VOLTA})

*Público / WhatsApp-ready.*

**Saída:**
```json
{
  "viagens": [
    {
      "veiculo_id": "ONIBUS-01",
      "tipo": "IDA",
      "status": "EM_ROTA",
      "ponto_atual": "Rodoviaria",
      "ponto_ordem_atual": 2,
      "total_pontos": 4,
      "proximo_ponto": "Ponto Central",
      "atualizado_em": "2026-06-10 12:30:00"
    }
  ]
}
```

---

## 🛡️ 4. Regras de Integridade e Validação

1. **Unicidade:** Um aluno não pode ter duas reservas ativas para a mesma data (garantido pelo ID composto `{cpf}_{data}`).
2. **Minimização (LGPD):** Não é permitida a coleta de e-mail pessoal, telefone ou endereço nesta fase do MVP. O CPF é dado contratual já existente.
3. **Segurança:** As rotas de consulta da gestora (`/api/painel`) e do motorista (`/api/checklist`) exigem o Header `X-Admin-Token`.
4. **Hard Lock:** Reservas para a data corrente são bloqueadas após o horário de corte configurável (padrão: 14h).
5. **Capacidade:** O check-in deve ser rejeitado quando o veículo atingir sua capacidade máxima, descontadas as vagas de exceção.

---

## 🛂 5. Protocolo de Governança para Agentes

- **Ana (Backend):** Você está proibida de criar migrações de banco ou rotas que retornem dados fora deste esquema. Use nomes descritivos em português conforme este documento.
- **José (Frontend):** Seus `inputs` no `index.html` e os nomes de chaves no `fetch()` devem ser idênticos aos nomes dos campos desta constituição.
- **Maria (Auditora):** Reprove qualquer código que introduza campos não documentados ou que viole a regra de minimização de dados.

---

### 💡 Por que este arquivo é vital?

O `SCHEMA.md` elimina o **Vibe Coding** desordenado onde a IA "adivinha" os nomes das colunas. Ele funciona como o alicerce técnico que permite que o frontend e o backend sejam construídos em paralelo com a certeza de que "conversarão" a mesma língua.
