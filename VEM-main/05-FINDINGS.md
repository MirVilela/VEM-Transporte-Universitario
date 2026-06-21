# 🧠 05-FINDINGS.md: Memória Técnica e Log de Autocura

## 🎯 1. Propósito e Uso

Este arquivo é o **Cérebro de Recuperação** do projeto. Sempre que ocorrer um erro de execução, bug visual ou inconsistência de lógica, o erro deve ser colado aqui antes de solicitar a correção à IA.

**Protocolo de Autocura:**

1. Copie o erro/traceback do terminal ou console.
2. Cole na seção **"Log de Incidentes"** abaixo.
3. Invoque a IA com o comando: *"Analise os erros no FINDINGS.md, identifique a causa raiz e aplique uma correção cirúrgica no código"*.

---

## 📋 2. Log de Incidentes e Erros (The Log)

*Utilize esta tabela para registrar falhas técnicas e comportamentais da IA durante as sessões.*

| Data | Sessão (VCC) | Descrição do Erro / Traceback | Causa Raiz | Correção Cirúrgica Aplicada |
| :--- | :--- | :--- | :--- | :--- |
| [Data] | [ID-VCC] | [Cole o erro aqui] | [Ex: Alucinação de biblioteca] | [Resumo da mudança] |

---

## 🔬 3. Análise de Causa Raiz (Root Cause) e Padrões

*Espaço para Maria (Revisora) ou Tiago (QA) documentarem por que erros recorrentes estão acontecendo.*

* **Padrão Detectado:** (Ex: A IA insiste em usar caminhos relativos em vez de `os.path.abspath`) [histórico de conversa].
* **Ação Preventiva:** (Ex: Reforçar a regra no `VIBE_MANIFEST.md` e no Seed Prompt da Ana).

---

## 💡 4. Decisões Técnicas e Trade-offs (Findings)

*Conforme as Karpathy Guidelines ("Think Before Coding"), registre aqui as premissas assumidas antes de grandes mudanças [histórico de conversa].*

* **Decisão:** Uso de SQLite puro sem ORM.
  * **Justificativa:** Garantir latência zero e seguir a regra de simplicidade 80/20.
* **Decisão:** Design Glassmorphism Mobile-First.
  * **Justificativa:** Foco na experiência do usuário Lucas (Alunos) para registros rápidos.
* **Decisão Validada:** Uso de SQLite em modo WAL suporta concorrência perfeitamente.
  * **Justificativa:** Teste de estresse realizado com sucesso (100 requisições concorrentes de cadastro no backend via threads em ~2.5 segundos, zero erros e sem bloqueio de concorrência). A arquitetura atual se provou robusta e a prova de carga.

---

## 🚧 5. Devedor Técnico e Lições Aprendidas

*O que ficou para o próximo giro do PDCA ou o que aprendemos que não deve ser repetido.*

1. **Lição:** Nunca importar fontes externas via CDN para manter o princípio **Offline-First**.
2. **Dívida:** O campo 'Telefone' solicitado pela Ana será implementado na Fase 7 (Evolução).

---

### 🛂 Instrução para a IA
>
> *"Antes de cada correção, consulte as seções 2 e 4 deste arquivo para garantir que a nova solução não repita erros do passado e mantenha as decisões arquiteturais já validadas"*.
