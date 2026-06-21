# 🧠 SKILL.md: Base de Conhecimento e Padrões Técnicos

## 🏛️ 1. Engenharia de Requisitos (Taxonomia VEM)

Os requisitos devem ser classificados seguindo a estrutura rigorosa da Engenharia de Software para eliminar ambiguidades.

* **RU (Requisitos de Usuário):** Descrições abstratas e genéricas das necessidades do cliente, escritas em linguagem natural e voltadas para *stakeholders*.
* **RS (Requisitos de Sistema):** Detalhamentos técnicos e específicos, escritos em linguagem natural estruturada (templates), que servem como contrato de implementação.
* **RF (Requisitos Funcionais):** Descrevem o que o sistema deve fazer (funções e serviços) e como deve reagir a entradas específicas.
* **RN (Regras de Negócio):** Declarações que definem ou restringem a operação da empresa, independentemente do software (ex: "Um aluno só pode ter uma reserva ativa por data de viagem").
* **RNF (Requisitos Não Funcionais):** Atributos de qualidade que descrevem *como* o sistema deve operar (ex: performance, segurança, usabilidade).

## ⚖️ 2. Categorias de Prioridade

Essenciais para gerenciar o escopo e aplicar a **Regra 80/20** (80% do valor com 20% do código).

1. **Essencial:** Funcionalidades imprescindíveis; sem elas, o sistema não faz sentido e não opera conforme seu objetivo.
2. **Importante:** Requisitos necessários, mas o sistema pode operar temporariamente com lacunas caso não sejam implementados de imediato.
3. **Desejável:** Funcionalidades de baixo impacto na operação básica, geralmente deixadas para versões futuras (giros do PDCA).

## ♿ 3. Acessibilidade Digital (Padrão WCAG)

Toda interface deve respeitar os princípios fundamentais **POUR** da W3C para garantir inclusão digital nível **AA** (Padrão Ouro).

* **Perceptível (Perceivable):** Informações apresentadas de forma que os usuários possam perceber (ex: textos alternativos, contrastes elevados).
* **Operável (Operable):** Interface navegável via teclado e funcional em diversos dispositivos.
* **Compreensível (Understandable):** Linguagem clara, intuitiva e previsível.
* **Robusto (Robust):** Compatível com tecnologias assistivas e leitores de tela.

## 🧪 4. Padrões de Teste (Modelo AAA)

Todos os testes unitários e integrados gerados pelos agentes (como o Tiago) devem seguir rigorosamente este padrão.

* **Arrange (Organizar):** Configurar o estado do teste, mocks e entradas necessárias.
* **Act (Agir):** Executar a unidade de código que está sendo testada.
* **Assert (Verificar):** Validar se o comportamento ou saída corresponde exatamente à expectativa.

## 🤖 5. Spec-Driven Development (SDD)

O fim do "vibe coding" desordenado; a documentação técnica é o centro do fluxo de desenvolvimento.

* **Definição de Escopo:** Instruir a IA sobre os limites exatos da tarefa para evitar refatoração desnecessária.
* **Redução de Ambiguidade:** Substituir termos vagos por restrições objetivas.
* **Preservação de Contexto:** Manter o conhecimento vivo em artefatos (.md) e não apenas no histórico volátil do chat.
* **Mudanças Cirúrgicas:** Alterar estritamente o necessário (**Karpathy-style**), respeitando o código existente.

---

## 🗺️ 6. Modelagem e Arquitetura (UML)

Os agentes devem ser capazes de interpretar e gerar diagramas em **Mermaid.js** para validar a lógica antes da implementação.

* **Diagrama de Caso de Uso (DCU):** Visão funcional de quem faz o quê no sistema.
* **Diagrama de Classes:** Estrutura estática e relações entre entidades.
* **Diagrama de Sequência:** Detalhamento da interação entre objetos e APIs ao longo do tempo.

---
**💡 Instrução para a IA:** Utilize este arquivo como seu manual de referência primário. Em caso de dúvida sobre como classificar um requisito ou estruturar um teste, a prioridade é o que está definido aqui.
