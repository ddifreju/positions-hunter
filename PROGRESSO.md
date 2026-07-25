# Progresso — MatchVagas

## Fase 0 — Fundação (concluída)

### Feito
- Repositório git local iniciado e enviado para https://github.com/ddifreju/positions-hunter; `.gitignore` criado e commitado antes de qualquer outro arquivo (R4).
- Estrutura de pastas: `app/` (entrada Streamlit), `src/matchvagas/` (lógica), `sql/` (schema), `tests/`.
- `requirements.txt`, `README.md`, `.env.example` (sem valores reais), `.env` local preenchido (Supabase, Gemini, Groq) e confirmado fora do controle de versão.
- `.claude/agents/` com os três agentes: `arquiteto`, `construtor`, `validador`.
- `CURADORIA.md` — 4 candidatos da Seção 5 avaliados (1 não localizado). `anthropic-skills:docx` aprovada para uso na Fase 4 (autorização ampla dada pela Jessica/Juliana para adoções futuras, mas seguimos registrando cada uma em `CURADORIA.md` e sinalizando qualquer coisa que peça credencial ou acesse domínio desconhecido).
- Função `gerar(prompt, tarefa)` implementada em `src/matchvagas/ia.py`, com roteamento por tarefa e fallback entre Gemini e Groq (Seção 6). Modelo do Gemini ajustado de `gemini-2.5-flash` (fixo, descontinuado para novas chaves) para o alias `gemini-flash-latest`/`gemini-pro-latest`, que segue a versão atual automaticamente.
- `sql/schema.sql` — schema inicial da Seção 7.3, revisado pelo `arquiteto` (cópia fiel, sem alterações) e aplicado no Supabase pela Jessica/Juliana via SQL Editor.
- Ambiente local: venv criado, dependências instaladas (`supabase`, `google-genai`, `groq`, `python-dotenv`, `pytest`).

### Critério de pronto — verificado
`pytest` rodando os 3 testes: conexão Supabase (lê e escreve `usuarias`) e `gerar()` respondendo via Gemini e via Groq. Todos passando.

```
tests/test_conexao_supabase.py::test_escreve_e_le_usuaria PASSED
tests/test_ia.py::test_gemini_responde PASSED
tests/test_ia.py::test_groq_responde PASSED
```

### O que quebrou e como foi resolvido
- Nome de modelo do Gemini hardcoded (`gemini-2.5-flash`) retornou 404 "no longer available to new users" — resolvido trocando para os aliases `-latest`, que a Google mantém apontando para o modelo vigente.
- Aplicar o schema exigiria a senha do Postgres, que não pedi (fica só com ela no gerenciador de senhas) — resolvido pedindo para ela rodar o SQL direto no SQL Editor do painel do Supabase.

### Pendente
Nada bloqueando. Fase 0 fechada.

## Próximo passo
Aguardar ok para começar a Fase 1 (fontes de vaga: Remotive, RemoteOK, Arbeitnow, Adzuna, Jooble, Himalayas, We Work Remotely).
