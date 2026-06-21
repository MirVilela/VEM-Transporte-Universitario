# 📝 02-DERS_MESTRE.md: Especificação Mestre de Requisitos

## 📑 1. Identificação e Controle de Versão
- **Projeto:** Sistema Preditivo de Transporte Universitário (SPTU).
- **Versão:** 1.0 (MVP - Progressive Web App).
- **Responsáveis:** Equipe de Engenharia.

---

## 🎯 2. Visão Geral e Escopo
- **Objetivo Central:** Automatizar a coleta de intenção de viagem dos estudantes via PWA para dimensionamento exato e antecipado da frota, eliminando o desperdício de assentos vazios.
- **Fora de Escopo:** Aplicativos nativos, recuperação complexa de senhas e integrações de mensageria externa.

---

## 👥 3. Requisitos de Usuário (RU)
- **RU01:** O aluno necessita de um acesso rápido sem formulários longos de cadastro, utilizando dados contratuais já existentes (CPF) para agendar sua semana.
- **RU02:** O aluno necessita de uma tela onde consiga definir assimetrias de trajeto de forma independente (só ida, só volta, ou ida/volta) para cada dia da semana.
- **RU03:** A gestão necessita visualizar instantaneamente a recomendação de frota ideal baseada na consolidação diária das reservas dos alunos.
- **RU04:** A gestão necessita que o embarque de retorno seja validado estritamente por ordem de chegada à porta do veículo, com exceção de alunos de locais distantes (vagas garantidas).
- **RU05:** O motorista necessita de uma interface de "clique único" para aprovar o embarque dos alunos até a capacidade máxima do seu veículo se esgotar.
- **RU06:** O aluno necessita receber avisos e comunicados importantes (como mudanças de trajeto ou interdições) de forma centralizada e destacada.
- **RU07:** O aluno necessita saber a localização aproximada do veículo durante o trajeto (via pontos de referência) sem depender de grupos de WhatsApp.

---

## ⚙️ 4. Requisitos de Sistema (RS)
- **RS01:** O sistema de autenticação deve validar o login cruzando o CPF do aluno com um PIN de 4 dígitos (com geração de PIN inicial atrelada ao próprio documento).
- **RS02:** **[RESTRIÇÃO ESTRITA DE BANCO]** O banco de dados deve utilizar o sistema de codificação manual para identificação. O uso de chaves primárias (PK) auto-incrementais está explicitamente proibido. O CPF do aluno atuará como a chave primária imutável nas tabelas relacionais.
- **RS03:** O sistema executará um bloqueio sistêmico ("Hard Lock") em um horário configurável (ex: 14h), rejeitando marcações na interface do aluno para a data corrente.
- **RS04:** O sistema deve suportar o "Check-in Dinâmico", onde a lista de retorno no celular do motorista não define quem entra no "Ônibus 1" previamente, mas vai abatendo o limite de assentos conforme a confirmação física.
- **RS05:** O sistema deduzirá antecipadamente da capacidade total do veículo as vagas marcadas pela gestora com a tag `[Exceção/Reserva]`.
- **RS06:** O sistema deve suportar um mural de avisos globais (máximo 10 ativos), permitindo publicação pela gestora com expiração automática por data ou arquivamento manual.
- **RS07:** O sistema deve permitir que o motorista registre, com um único clique, o ponto pré-cadastrado em que o veículo se encontra para atualizar a interface do aluno via polling automático (30s).

---

## ✅ 5. Requisitos Funcionais (RF) e Priorização

| ID | Descrição do Requisito | Tipo | Prioridade | Critério de Aceite (Sucesso) |
| :--- | :--- | :--- | :--- | :--- |
| **RF01** | Autenticação Baseada em Contrato. | RS | **Essencial** | Aluno faz login apenas com CPF numérico e PIN de 4 dígitos. |
| **RF02** | Calendário de Viagens (PWA). | RS | **Essencial** | Interface mobile onde o aluno seleciona o trajeto para os dias úteis. |
| **RF03** | Painel de Alocação de Frota (Ana). | RS | **Essencial** | Dashboard converte total de alunos em sugestão de frota (ex: 2 Ônibus, 1 Van). |
| **RF04** | Flag de Vaga de Exceção. | RS | **Importante** | Gestão marca alunos de pontos rurais/distantes, blindando seus assentos. |
| **RF05** | Checklist Dinâmico (Motorista). | RS | **Essencial** | Interface onde o motorista seleciona nomes até travar no limite físico do ônibus. |
| **RF06** | Mural de Avisos. | RS | **Importante** | Gestora publica avisos exibidos como banners na tela do aluno. |
| **RF07** | Rastreamento de Viagem (Tracking). | RS | **Importante** | Motorista marca ponto de rota; tela do aluno exibe barra de progresso. |

---

## 📏 6. Regras de Negócio (RN)

| ID | Descrição da Regra | Requisito Relacionado |
| :--- | :--- | :--- |
| **RN01** | **Ordem de Chegada Física:** A ocupação do veículo de retorno (ex: Ônibus 01) não aceita reservas online de assento. A vaga é confirmada mediante presença física na porta do ônibus. | RU04, RS04 |
| **RN02** | **Blindagem de Exceções:** Passageiros com "Vaga Reservada" subtraem assentos disponíveis antes do embarque da fila comum iniciar. | RF04, RS05 |
| **RN03** | **Minimização de Ociosidade:** O cálculo da frota deve buscar o menor índice de assentos vazios, combinando as capacidades padronizadas dos veículos disponíveis. | RF03 |
| **RN04** | **Política de No-Show:** Faltas geram relatórios gerenciais automáticos; punições não são sistêmicas, ficando a critério da análise humana. | RF05 |

---

## 🛡️ 7. Requisitos Não Funcionais (RNF)

| ID | Nome / Atributo | Categoria | Prioridade | Descrição Técnica |
| :--- | :--- | :--- | :--- | :--- |
| **RNF01** | Acessibilidade Mobile (PWA) | Usabilidade | **Essencial** | A interface do aluno deve sugerir instalação na tela inicial do smartphone. |
| **RNF02** | Tolerância Offline (Motorista) | Confiabilidade | **Importante** | A lista de passageiros deve carregar em cache para permitir chamadas sem internet ativa. |
| **RNF03** | Operação Mono-Mão | Usabilidade | **Essencial** | Os botões de confirmação de ida/volta e check-in devem possuir zonas de toque (touch targets) de no mínimo 48x48px. |

---

## ⚖️ 8. Diretrizes Karpathy de Implementação (VEM)
1. **Pense antes de codar:** Explicite suposições no `FINDINGS.md`.
2. **Sem Auto-Incremento:** Respeite o **RS02** sob qualquer circunstância.
3. **Simplicidade Radical:** Utilize APIs de armazenamento local (LocalStorage/IndexedDB) para o cache do motorista em vez de bibliotecas pesadas.

---

## 🔗 9. Matriz de Rastreabilidade Simples
*Mapeamento para garantir a integridade entre o problema e a solução.*

* **RU01 (Acesso Rápido)** → RF01 (Autenticação CPF), RS02 (Chave Manual).
* **RU02 (Definir Assimetrias)** → RF02 (Calendário PWA), RS03 (Hard Lock).
* **RU03 (Visualizar Frota)** → RF03 (Painel de Alocação), RN03 (Minimizar Ociosidade).
* **RU04 (Ordem de Chegada)** → RF04 (Vaga de Exceção), RN01 (Ordem Física), RN02 (Blindagem).
* **RU05 (Check-in Fácil)** → RF05 (Checklist Dinâmico), RS04 (Check-in Dinâmico), RNF02 (Tolerância Offline).
* **RU06 (Comunicados e Avisos)** → RF06 (Mural de Avisos), RS06.
* **RU07 (Localização do Veículo)** → RF07 (Rastreamento de Viagem), RS07.