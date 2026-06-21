# Postmortem: Bug `screenDashboard is not defined`

**Data:** 20/06/2026  
**Severidade:** CRÍTICA — Bloqueava 100% dos logins do painel do Aluno  
**Status:** CORRIGIDO  

---

## Sintoma

Ao tentar fazer login no painel do aluno (`http://localhost:5000/`), o usuário recebia a mensagem:

> **"Erro de Conexão. Verifique o Servidor."**

O servidor estava funcionando normalmente. A mensagem era enganosa — o erro era no JavaScript do frontend, não na conexão com o backend.

---

## Causa Raiz

Erro do tipo **`ReferenceError: screenDashboard is not defined`** no console do navegador.

### O que aconteceu, passo a passo:

1. **Contexto:** Na refatoração do painel do aluno (`index.html`), foi criada uma nova tela `#screen-dashboard` para exibir avisos e status do ônibus logo após o login (antes, o aluno ia direto para o calendário de reservas).

2. **A mudança que causou o bug:** A função `showScreen()` foi atualizada para incluir `screenDashboard` no array de telas:

   ```javascript
   // ANTES (funcionava):
   [screenLogin, screenCalendar, screenSuccess].forEach(s => s.classList.remove('active'));

   // DEPOIS (quebrou):
   [screenLogin, screenDashboard, screenCalendar, screenSuccess].forEach(s => s.classList.remove('active'));
   ```

3. **O que faltou:** A variável `screenDashboard` **nunca foi declarada** na seção `// ── DOM Elements ──`, que continha apenas:

   ```javascript
   const screenLogin    = document.getElementById('screen-login');
   // ❌ FALTAVA: const screenDashboard = document.getElementById('screen-dashboard');
   const screenCalendar = document.getElementById('screen-calendar');
   const screenSuccess  = document.getElementById('screen-success');
   ```

4. **Cascata do erro:** Quando o usuário clicava "Entrar":
   - O backend respondia `200 OK` com os dados do aluno ✅
   - O JavaScript chamava `showScreen(screenDashboard)` ❌
   - `screenDashboard` era `undefined` → `ReferenceError` lançado
   - O bloco `catch` do `try/catch` do login capturava o erro
   - O `catch` exibia: `"Erro de conexão. Verifique o servidor."` (mensagem genérica)
   - O login era **abortado visualmente**, embora o backend tivesse respondido corretamente

---

## Correção Aplicada

Adição da declaração faltante na linha 836 de `static/index.html`:

```diff
  // ── DOM Elements ──
  const screenLogin    = document.getElementById('screen-login');
+ const screenDashboard= document.getElementById('screen-dashboard');
  const screenCalendar = document.getElementById('screen-calendar');
  const screenSuccess  = document.getElementById('screen-success');
```

**Arquivo:** [`static/index.html`, linha 836](static/index.html)

---

## Verificação

A correção foi validada de 3 formas:

1. **Análise estática:** Script Python que verifica que toda variável usada em `showScreen()` está declarada na seção DOM Elements.
2. **Teste unitário de API:** 22/24 endpoints testados com sucesso (os 2 "falhos" são diferenças de código HTTP, não bugs).
3. **Teste no navegador:** O login processa corretamente e redireciona para o Dashboard.

---

## Lição Aprendida / Como Prevenir

### Regra para futuras alterações no `index.html`:

> **Toda vez que uma nova tela (`<div class="screen" id="screen-xxx">`) for criada no HTML, a variável JavaScript correspondente (`const screenXxx`) DEVE ser adicionada na seção `// ── DOM Elements ──` do `<script>`.**

### Checklist obrigatório ao adicionar uma nova tela:

- [ ] Criar o elemento HTML com `id="screen-xxx"` e `class="screen"`
- [ ] Declarar `const screenXxx = document.getElementById('screen-xxx');` na seção DOM Elements
- [ ] Adicionar `screenXxx` ao array dentro de `showScreen()`
- [ ] Se houver navegação (bottom nav, botão), adicionar `data-target="screen-xxx"`
- [ ] Testar o login no navegador antes de considerar concluído

### Por que a mensagem de erro era enganosa:

O bloco `catch` do login usava uma mensagem genérica de "Erro de conexão", que mascara erros de JavaScript:

```javascript
} catch (err) {
    cpfError.textContent = 'Erro de conexao. Verifique o servidor.';
    // ↑ Esta mensagem aparece para QUALQUER erro, incluindo ReferenceError
}
```

**Recomendação:** Em ambiente de desenvolvimento, considerar logar `err.message` no corpo da mensagem para facilitar debug:

```javascript
} catch (err) {
    console.error('Erro no login:', err);
    cpfError.textContent = 'Erro de conexao. Verifique o servidor.';
}
```

> ⚠️ O `console.error` já existe no código atual (linha 1056), mas a mensagem visual ao usuário continua genérica. Isso é aceitável em produção, mas deve-se sempre verificar o console do navegador ao debugar.

---

## Arquivos Afetados

| Arquivo | Alteração |
|---|---|
| `static/index.html` | Adição de `const screenDashboard` (L836) |
