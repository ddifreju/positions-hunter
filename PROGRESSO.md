# Progresso — MatchVagas

## Fase 0 — Fundação (em andamento)

### Feito
- Repositório git local iniciado; `.gitignore` criado e commitado antes de qualquer outro arquivo (R4).
- Estrutura de pastas: `app/` (entrada Streamlit), `src/matchvagas/` (lógica), `sql/` (schema), `tests/`.
- `requirements.txt`, `README.md`, `.env.example` (sem valores reais).
- `.claude/agents/` com os três agentes: `arquiteto`, `construtor`, `validador`.
- `CURADORIA.md` — 4 candidatos da Seção 5 avaliados (1 não localizado). Recomendação "adotar agora": `anthropic-skills:docx` para a Fase 4, aguardando aprovação.
- Função `gerar(prompt, tarefa)` implementada em `src/matchvagas/ia.py`, com roteamento por tarefa e fallback entre Gemini e Groq (Seção 6).
- `sql/schema.sql` — schema inicial copiado da Seção 7.3, pronto para revisão do `arquiteto` antes de aplicar no Supabase.
- Testes de critério de pronto escritos: `tests/test_conexao_supabase.py` (lê/escreve no Supabase) e `tests/test_ia.py` (gerar() responde via dois provedores).

### Bloqueado — aguardando setup manual (Seção 3.1 do briefing)
Estes testes **não foram executados ainda** porque dependem de chaves que só a humana pode gerar:
- `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` — projeto Supabase ainda não criado.
- `GEMINI_API_KEY` — chave do Google AI Studio ainda não gerada.
- `GROQ_API_KEY` — não pedida ainda (Groq é o segundo provedor da função `gerar()`; passo a passo será dado quando as outras chaves chegarem).
- URL do repositório GitHub — ainda não informada, então nenhum push foi feito.
- Schema ainda não aplicado no Supabase (não existe projeto para aplicar).

### Pendente para fechar a Fase 0
1. Receber URL do repo GitHub, `.env` preenchido (Supabase + Gemini), e então: aplicar `sql/schema.sql` no Supabase, rodar `pytest` e confirmar que os dois testes de critério de pronto passam.
2. `arquiteto` revisar o schema antes de aplicar.
3. Reportar fechamento da Fase 0 e pedir ok para começar a Fase 1.

## Próximo passo
Aguardando as chaves e a URL do repositório (checklist já enviado) para concluir e fechar a Fase 0.
