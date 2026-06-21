# 01-NORTH_STAR.md: Intenção e Limites do Projeto

## 🎯 1. Intenção Central (The North Star)
Uma única frase que define o sucesso absoluto do projeto.

**R:** Otimização preditiva e autônoma da alocação de frota de transporte intermunicipal universitário para erradicar a ociosidade de assentos, utilizando uma interface web (PWA) de altíssima adesão para estudantes.

## 😫 2. O Problema Real (A Dor)
Qual é a dor do mundo real que estamos resolvendo?

**R:** O modelo atual via grupos de WhatsApp oferece uma janela logística inviável (1h30) para calcular e alocar a frota. Isso resulta em ociosidade financeira (despachar ônibus vazios), atritos na comunicação, omissão de assimetrias (alunos que só vão ou só voltam) e total falta de controle e justiça sobre o embarque de retorno em dias de alta demanda.

## 👥 3. Público-Alvo (As Personas)
O sistema é desenhado para atender às necessidades específicas destes três perfis:

* **João (O Estudante):** Deseja garantir sua vaga de ida e/ou volta marcando os dias da semana em menos de 10 segundos através de um PWA no celular, acessando via seu CPF e um PIN simples.
* **Ana (A Gestora):** Precisa visualizar a volumetria exata de passageiros com dias de antecedência para acionar a frota correta (ônibus, micro-ônibus ou vans) e gerenciar as vagas de exceção (alunos de rotas rurais/distantes).
* **Carlos (O Motorista):** Precisa de um checklist digital rápido para realizar a auditoria de embarque (física e real) no momento em que os alunos entram no veículo.

## 🔍 4. Checklist de Descoberta (5 Questões)
Critérios fundamentais que a IA deve respeitar ao propor soluções:

* **Fonte do Dado:** O celular do próprio aluno por meio de um Progressive Web App (PWA) de carregamento ultrarrápido.
* **Entrega:** Persistência transacional imediata e atualização de painel gerencial da frota em tempo real.
* **Regra de Ouro:** O fechamento de listas diárias deve ser mecânico e implacável no horário de corte (ex: 14h), impedindo reservas fora do prazo.
* **Resiliência:** O sistema do motorista para validação de embarque deve manter a lista em cache (offline-first) para operar em rodoviárias ou campi com baixo sinal de internet.
* **Interface:** Foco mobile-first, limpa, botões de alto contraste e navegação livre de menus complexos.

## 🚫 5. Limites e Fora de Escopo
Para evitar o "scope creep" e manter a simplicidade estrutural.

* **NÃO** faremos integração com APIs ou bots de WhatsApp nesta fase de MVP.
* **NÃO** criaremos aplicativos compilados para lojas (App Store/Play Store).
* **NÃO** utilizaremos frameworks pesados no front-end se o Vanilla/HTML simples resolver.
* **NÃO** utilizaremos métodos de autenticação complexos (e-mail de confirmação ou OAuth); o acesso será exclusivamente por documento de contrato (CPF).

## ⚖️ 6. Mindset de Simplicidade (Karpathy Style)
Este projeto segue a Regra 80/20: 80% do valor operacional será entregue com 20% do código.
Foco: Um aplicativo web de acesso direto (CPF + PIN) onde o aluno seleciona o calendário da semana. Esses dados alimentam diretamente o painel da gestora, que cruza a capacidade dos veículos e exporta a lista de check-in dinâmico para os motoristas lidarem com o embarque físico.

### 🛂 Instrução para a IA
> "Antes de iniciar a Fase de Desenvolvimento, leia este arquivo. Qualquer funcionalidade sugerida que fira os limites do Item 5 ou o Mindset do Item 6 deve ser descartada imediatamente."