# 🏁 Projeto VEM — Arquitetura Orientada a Agentes

> **Filosofia:** Do problema real ao deploy em produção — unindo metodologias para formar engenheiros, não digitadores de código.

Este projeto utiliza a metodologia **AI-First Engineering**, integrando **Engenharia de Requisitos**, **Spec-Driven Development (SDD)** e as diretrizes de simplicidade **Karpathy-style**. O objetivo é transformar problemas reais em MVPs resilientes através de uma linha de montagem estruturada entre humanos e agentes de IA.

## 🏗️ Arquitetura Padrão Ouro

Este projeto separa a aplicação clássica dos componentes de inteligência:

* **Agente (`/agente`):** Lógica proativa e plugins de ação.
* **Memory (`/rag`):** Consulta a base de conhecimento (PDFs/MDs) para evitar alucinações.
* **Tools (`mcp_server.py`):** Protocolo MCP para acesso seguro ao banco de dados SQLite local.

## 🗺️ Mapa da Memória (RAG)

Os arquivos em `/rag/memoria/` e os `.md` da raiz são a Única Fonte da Verdade.

1. **`00-README.md` (Ponto de Partida)**: Consolidação metodológica e governança do projeto (Vibe Engineering Method).
2. **`01-NORTH_STAR.md` (Intenção e Limites)**: O arquivo que define o "Norte" do projeto, garantindo clareza total sobre o problema antes de qualquer linha de código. Serve para eliminar a ambiguidade e estabelecer os limites do MVP (Mínimo Produto Viável).
3. **`02-DERS_MESTRE.md` (Contrato Técnico Vivo)**: O contrato técnico vivo do projeto, servindo como a "única fonte da verdade" sobre o que o sistema deve fazer. Transforma a dor do usuário em especificações acionáveis para os agentes de IA, estruturadas nos quatro pilares da Engenharia de Requisitos: Identificar, Rastrear, Controlar e Comunicar.
4. **`03-FRONTEND_GUIDE.md` (Diretrizes do José)**: O manual de diretrizes para o agente José, responsável pela interface e experiência do usuário (UI/UX) dentro da metodologia VEM. Garante que a interface seja premium, acessível (WCAG POUR) e livre de complexidade desnecessária (*bloat*).
5. **`04-BACKEND_GUIDE.md` (Diretrizes da Ana)**: O manual de diretrizes para a agente Ana, responsável pela construção do motor, lógica de negócios e persistência de dados. Garante que o "coração" do sistema seja robusto, resiliente (Offline-First) e siga padrões rigorosos de simplicidade técnica (Flask, SQLite e caminhos absolutos).
6. **`05-FINDINGS.md` (Memória e Diário de Autocura)**: Atua como a memória técnica e o diário de autocura do projeto. Sua função principal é registrar erros e servir de base de conhecimento para que a IA analise padrões de falhas e aplique correções cirúrgicas, evitando retrabalho e código "Frankenstein".
7. **`06-WIREFRAME_IDEAS.md` (Arquitetura Visual)**: O artefato central da Fase 3 (Projeto e Arquitetura) da metodologia VEM. Traduz os requisitos técnicos em uma visão visual e arquitetural (esboços Mermaid/Texto aprovados), garantindo que José (Frontend) e Ana (Backend) trabalhem em perfeita sintonia.
8. **`SCHEMA.md` (Constituição dos Dados)**: Define a estrutura técnica inegociável sob o princípio *"JSON is Law"* (O JSON é a Lei), servindo como contrato de API que deve ser espelhado tanto no banco de dados da Ana (Backend) quanto nos formulários do José (Frontend), garantindo integração perfeita.
9. **`VIBE_MANIFEST.md` (Regras Inegociáveis)**: O documento de governança técnica que estabelece as regras duras (*Hard Rules*) do projeto. Integra as diretrizes de simplicidade *Karpathy-style* para garantir que o desenvolvimento seja linear, resiliente e livre de sobre-engenharia.
10. **`CLAUDE.md` (Configurações de Sistema e Personas)**: O manual de comportamento, governança e identidade para todos os agentes de IA que operam no repositório. Integra as Karpathy Guidelines com a metodologia VEM para manter o desenvolvimento linear, seguro e sob controle.
11. **`SKILL.md` (Biblioteca de Padrões Técnicos)**: Atua como base de conhecimento (RAG) consolidando os padrões acadêmicos e profissionais (WCAG, LGPD, Padrão AAA) que os agentes de IA devem dominar para garantir o desenvolvimento segundo as melhores práticas.
12. **`PROMPTS.md` (Repositório de Prompts Mestres)**: O roteiro de execução técnica da metodologia VEM, contendo os prompts mestres testados para cada persona do projeto. Funciona como guia de "Ship" (Fase 6) para entrega de código funcional e resiliente.
13. **`VCC_TEMPLATE.md` (Contrato de Sessão)**: O contrato do Vibe-Coding Canvas para governança de cada sessão de desenvolvimento. Deve ser preenchido antes de qualquer interação para garantir que o *vibe coding* seja estruturado, rastreável e focado em resultados reais.
14. **`GUIA_DO_USUARIO.md` (Guia Humano do Sistema)**: Documento de fácil compreensão para humanos que explica como rodar o sistema, as credenciais de teste, o funcionamento de cada tela e as regras importantes. **Deve ser atualizado** sempre que houver mudanças em funcionalidades, credenciais, rotas ou frota.

## 🛂 Protocolo de Agentes (Skills)

Ao operar neste repositório, a IA assume papéis específicos para garantir a separação de preocupações:

* **José (Frontend):** Interfaces modernas, responsivas e acessíveis (WCAG POUR).
* **Ana (Backend):** Motores robustos, integridade de dados e logs detalhados.
* **Maria (Auditora):** Revisão de conformidade com LGPD, ética e qualidade de requisitos.
* **Tiago (QA):** Testes unitários e E2E seguindo o padrão AAA (Arrange, Act, Assert).

## ⚖️ Regras Karpathy Inegociáveis

* **Pense antes de codar:** Explicite suposições e aponte ambiguidades antes de gerar código.
* **Regra 80/20:** Entregue 80% do valor com 20% do código (evite "bloat").
* **Mudanças Cirúrgicas:** Altere apenas as linhas necessárias; não re-formate o que funciona.
* **Offline-First:** O sistema deve operar localmente, independente de internet.

## 🔄 Fluxo de Operação (SDD)

1. **Contexto:** Preencha um **VCC** (Vibe-Coding Canvas) para cada sessão.
2. **Build:** Execução via Personas, respeitando o `SCHEMA.md`.
3. **Check:** Validação manual e automatizada antes do commit.
4. **Ship:** Deploy após atualização da documentação de lições aprendidas.

## 📚 Guias de Estilo e Boas Práticas

Este projeto se baseia nas seguintes referências metodológicas e de engenharia:

### 1. Engenharia de Requisitos e Especificação

* **Spec-Driven Development (SDD)**: O padrão ouro para especificação de requisitos.
  * *Referência:* `https://github.com/git/spec-kit`

* **Engenharia de Requisitos 5ª Edição** (Artur Rezende): Referência fundamental para estruturação, rastreabilidade e controle de requisitos. Este guia fundamenta a metodologia VEM.

### 2. Desenvolvimento de Software e Arquitetura

* **The Missing Semester of Your CS Education (MIT)**: Cursos práticos sobre ferramentas essenciais de desenvolvimento.
  * *Referência:* (Curso online disponível em edX/MIT OpenCourseware)

* **Commit-Based Development** (Karpathy): Foco em commits atômicos e significado técnico.
  * *Referência:* (Artigos e discussões de Andrej Karpathy sobre Git e desenvolvimento)
* **Karpathy Guidelines**: Diretrizes de simplicidade, priorização de código essencial e evitação de complexidade.
  * *Referência:* (Série de tweets e postagens de blog de Andrej Karpathy sobre engenharia de software)
* **Superpowers (PSReadLine)**: Melhores práticas para linha de comando interativa e produtividade.
  * *Referência:* `https://github.com/Power-Shell-Plus/superpowers`
* **Multica AI**: Plataforma e ecossistema voltada ao gerenciamento ágil de sessões de codificação auxiliadas por agentes de IA e controle de Model Context Protocol (MCP).
  * *Referência:* `https://github.com/multica-ai/multica`
* **Multica Agent Skills**: Repositório de servidores MCP e habilidades modulares prontas para estender e otimizar a capacidade operacional de agentes autônomos.
  * *Referência:* `https://github.com/multica-ai/multica/tree/main/agent/mcp-server/skills/`

### 3. Design e Experiência do Usuário (UI/UX)

* **Glassmorphism**: Estilo de design com transparência e efeito de vidro fosco.
  * *Referência:* (Design trends e artigos sobre Glassmorphism)

* **Golden Ratio Layouts**: Design baseado na Proporção Áurea para interfaces harmoniosas.
  * *Referência:* (Design articles on Golden Ratio in UI/UX)
* **Material Design Guidelines**: Princípios de design de interface e componentes do Google.
  * *Referência:* (Oficial Material Design Guidelines website)
* **Human Interface Guidelines (Apple)**: Padrões de design para aplicativos Apple.
  * *Referência:* (Official Apple Human Interface Guidelines)
* **WCAG (Web Content Accessibility Guidelines)**: Diretrizes para acessibilidade na web.
  * *Referência:* (W3C WCAG official website)

* **Testar no futuro**
  * [anthropics/skills](https://github.com/anthropics/skills)

## ⚙️ Instalação do modo Caveman

A instalação do modo **Caveman** (uma ferramenta projetada para economizar ~75% dos tokens de saída) pode ser feita de duas formas principais, dependendo da sua preferência de uso.

### 🛠️ Requisitos Iniciais

* Certifique‑se de ter **Node.js ≥ 18** instalado na sua máquina.

---

### 🚀 Opções de Instalação

**Opção A – Como Plugin do Claude Code (Recomendado)**  
Instala as diretrizes como um plugin global, disponível em todos os projetos dentro do ambiente Claude Code.

```bash
# No terminal do Claude Code
marketplace add juliusbrussee/caveman
marketplace install juliusbrussee/caveman
```

**Opção B – Configuração por Projeto (via `CLAUDE.md`)**  
Aplica as regras do Caveman apenas ao projeto atual.

```bash
# Projeto novo
npx caveman-code@latest init

# Projeto existente (anexar ao `CLAUDE.md`)
npx caveman-code@latest init --append
```

---

### 🎮 Como Ativar e Usar

* **Ativar:** digite `/caveman` ou fale “talk like caveman”.
* **Níveis de compressão:** ajuste a intensidade com `/caveman lite`, `full`, `ultra` ou `wenyan`.  
* **Desativar:** digite “modo normal” ou “para caveman”.

> **Dica VEM:** durante a fase de **Build** ou demonstrações ao vivo, use o modo Caveman para respostas técnicas rápidas e diretas, focando na essência do código sem “enfeites” desnecessários.

## 📚 Fundamentação Teórica e Metodológica

* **Engenharia de Requisitos:** Guia completo de requisitos funcionais (RF) e não funcionais (RNF) com taxonomia (RU, RS) para eliminar ambiguidades.
* **Spec‑Driven Development (SDD):** A especificação precede a implementação; a IA atua como “estagiário proativo” que precisa de contexto estruturado para evitar alucinações.
* **MASP e PDCA:** Integração do ciclo PDCA e do Método de Análise e Solução de Problemas para melhoria contínua e foco na causa raiz.
* **Arquitetura de Agentes (Padrão Ouro):** Separação clara entre agente (core), MCP (ferramentas), RAG (memória), e plugins, garantindo governança e modularidade.
* **Governança (VCC & Prompts):** Vibe‑Coding Canvas (VCC) como contrato de sessão; prompts mestres para personas João (UI/UX), Ana (Backend) e Piloto (Deploy); “JSON is Law” via `SCHEMA.md`.
* **Eficiência (Modo Caveman & Mudanças Cirúrgicas):** Redução de consumo de tokens em até 75 % e alteração apenas das linhas necessárias, evitando código “Frankenstein”.
* **Estudo de Caso – Sistema Preditivo de Transporte Universitário (SPTU):** Aplicação prática com reserva semanal de vagas, alocação preditiva de frota e persistência local, demonstrando todo o fluxo da metodologia VEM.
