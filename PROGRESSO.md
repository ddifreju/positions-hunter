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

## Fase 1 — Fontes de vaga (concluída)

### Feito
- Testadas 5 fontes sem necessidade de chave: Remotive, RemoteOK, Arbeitnow, Himalayas e We Work Remotely (RSS). As 5 responderam com dados reais e válidos — não precisei pedir Adzuna/Jooble, já que o critério de pronto (mínimo 3) foi superado sem exigir cadastro extra da Jessica/Juliana.
- `src/matchvagas/etl/` — um coletor por fonte (`remotive.py`, `remoteok.py`, `arbeitnow.py`, `himalayas.py`, `weworkremotely.py`), todos normalizando pro formato da tabela `vagas`; `util.py` com limpeza de HTML da descrição (evita poluir o TF-IDF da Fase 3); `runner.py` orquestra a coleta, deduplica por `(plataforma, id_externo)` e grava via upsert no Supabase.
- `tests/test_etl.py` — smoke test por fonte (responde e normaliza nos campos certos) + teste de que o runner nunca produz duplicata antes de gravar.

### Critério de pronto — verificado
Rodei o runner duas vezes contra o Supabase real: primeira rodada gravou 633 vagas das 5 fontes, segunda rodada (idempotente) só somou 2 vagas novas — sem duplicata, confirmando o `unique(plataforma, id_externo)` do schema.

```
coletadas 633 vagas de 5/5 fontes
gravadas/atualizadas 633 vagas no Supabase
```

Distribuição: remotive 38, remoteok 100, arbeitnow 300 (limitado a 3 páginas), himalayas 98 (limitado a 5 páginas), weworkremotely 97.

### O que quebrou e como foi resolvido
- Primeira gravação falhou com "ON CONFLICT DO UPDATE command cannot affect row a second time" — a Himalayas repete vaga entre páginas quando o catálogo muda durante a coleta (paginação por offset instável, não é bug da fonte). Resolvido deduplicando por `(plataforma, id_externo)` antes do upsert; o teste correspondente checa essa invariante no nível do runner, não por fonte isolada.

### Pendente
Nada bloqueando. Adzuna/Jooble ficam registrados como opção futura se a cobertura das 5 fontes atuais se mostrar insuficiente — não pedi as chaves porque não precisei.

## Próximo passo
Aguardar ok para começar a Fase 2 (entrada de documentos e banco de evidências).
