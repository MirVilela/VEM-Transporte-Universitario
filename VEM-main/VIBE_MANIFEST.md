# 📜 VIBE_MANIFEST.md: Regras de Engenharia Inegociáveis

## 🧠 1. Mindset de Engenharia (Karpathy Guidelines)

*As diretrizes abaixo priorizam a **cautela sobre a velocidade** e a assertividade sobre a digitação rápida.*

* **Pense antes de Codar:** Nunca assuma nada silenciosamente. Se houver ambiguidade no requisito, a IA deve parar, listar suas suposições e pedir clarificação antes de agir.
* **Mudanças Cirúrgicas:** Altere estritamente as linhas necessárias para a tarefa ou correção. É terminantemente proibido reformatar arquivos inteiros, mudar estilos de aspas ou adicionar documentação não solicitada.
* **Simplicidade Radical (Regra 80/20):** Busque o código mínimo que resolva 80% do problema com 20% do esforço. Evite abstrações prematuras ou padrões de projeto complexos se uma solução linear resolver a dor.
* **Execução Orientada a Metas:** Toda tarefa deve ser transformada em uma meta verificável. Prefira o fluxo: "Escrever teste que reproduz o erro → Fazer o teste passar → Verificar ausência de regressões".

## ⚙️ 2. Restrições Técnicas de Build (The Law)

*Estas regras garantem a integridade do motor e a manutenibilidade do software.*

* **Offline-First:** O sistema deve operar 100% em rede local, sem depender de CDNs externas, APIs de nuvem ou internet para suas funções centrais.
* **Soberania do Dado (JSON is Law):** Nenhuma rota de API ou tabela de banco de dados pode divergir da estrutura definida no `SCHEMA.md`.
* **Caminhos Absolutos:** Utilize sempre caminhos absolutos (`os.path.abspath`) para persistência de dados e localização de arquivos estáticos, garantindo a execução independente da pasta de origem.
* **Limites de Granularidade:** Cada função deve ter, preferencialmente, **menos de 30 linhas**. Arquivos únicos não devem exceder **400 linhas**; se ultrapassarem, a IA deve sugerir a quebra em módulos no próximo giro do PDCA [320, historical context].

## ♿ 3. Padrões de Qualidade e Conformidade

*Diretrizes obrigatórias para os agentes José, Ana, Maria e Tiago.*

* **Acessibilidade POUR:** Toda interface deve ser auditada pelos princípios de ser **Perceptível, Operável, Compreensível e Robusto**, visando conformidade WCAG.
* **Padrão de Teste AAA:** Todos os testes gerados devem seguir o padrão **Arrange (Organizar), Act (Agir) e Assert (Verificar)**.
* **Segurança de Transmissão:** Dados sensíveis (senhas/tokens) nunca devem aparecer em URLs; utilize obrigatoriamente Headers seguros ou `sessionStorage`.

## 🚫 4. Gatilhos de Rejeição (Push Back)

*A IA deve "empurrar de volta" e alertar o humano caso:*

* Seja solicitado o uso de frameworks pesados (ex: React, Vue) quando HTML/JS Vanilla é suficiente.
* O usuário peça para ignorar regras de acessibilidade ou segurança por "pressa".
* A inclusão de uma biblioteca externa não tenha justificativa estratégica no `NORTH_STAR.md`.

---

**🛂 Protocolo de Auditoria:** Qualquer código que viole este manifesto será sumariamente reprovado pela agente **Maria (Revisora)**, exigindo uma correção cirúrgica imediata na linha de montagem [351, historical context].
