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

## Fase 2 — Entrada e banco de evidências (concluída)

### Feito
- `src/matchvagas/documentos.py` — extração de texto de PDF (pypdf) + upload no bucket privado `documentos` do Supabase Storage + registro em `documentos`.
- `src/matchvagas/evidencias.py` — geração de evidências com tags a partir de texto de documento via `gerar(tarefa="extracao_pdf")`, com R2 embutida no prompt.
- `src/matchvagas/entrevista.py` — Entrevista 1 (intenção): gera 5-6 perguntas a partir do resumo das evidências já registradas, registra resposta e gera evidência a partir dela.
- Usuária real `Juliana` criada no Supabase. Rodei o pipeline com o PDF do LinkedIn dela (`Profile (5).pdf`, tipo `linkedin`): **21 evidências** do documento + Entrevista 1 completa (6 perguntas respondidas, 6 evidências geradas) = **25 evidências no total**.
- R2 verificada manualmente: cruzei as 21 evidências do documento linha a linha com o texto extraído do PDF — todas com lastro real, nenhuma inventada.
- `tests/test_evidencias.py` e `tests/test_entrevista.py` — smoke tests com PDF/dados sintéticos (não reais) cobrindo a mecânica do pipeline.

### O que quebrou e como foi resolvido
- **Perguntas da Entrevista 1 saíam com jargão complexo** (ex.: "equilíbrio entre atuação técnica especialista (hands-on) e liderança/mentoria") — difícil de responder de bate-pronto. A Juliana pediu perguntas simples, uma ideia por vez. Reescrevi `PROMPT_PERGUNTAS_INTENCAO` exigindo linguagem do dia a dia, sem jargão, uma ideia por pergunta.
- **Evidências geradas direto da resposta bruta da entrevista saíam telegráficas e sem lastro de contexto** (ex.: resposta longa sobre decisão de arquitetura virou só "estudar sobre a regra de negócio"). Criei um prompt dedicado (`PROMPT_EVIDENCIA_RESPOSTA`, separado do prompt de extração de documento) que reescreve a resposta em linguagem corporativa amigável, preservando a substância, sem adicionar fato novo. Registrado como memória de feedback para reaplicar na Entrevista 2 (Fase 3).
- Ao regenerar as evidências de entrevista com o prompt novo, a exclusão das antigas esbarrou numa foreign key (`perguntas.gerou_evidencia_id`) — resolvido limpando a referência antes de deletar.

### Ponto em aberto — precisa da sua confirmação
Na resposta sobre decisão de arquitetura, você mencionou "**canunda**" (provável erro de transcrição por voz). O modelo interpretou como referência à ferramenta **Camunda** (motor de workflow) e gerou a evidência: *"Sente-se motivada na tomada de decisão sobre arquitetura de sistemas, avaliando a utilização de componentes, Camunda e serviços em nuvem como AWS ou Azure."* Isso é uma interpretação, não uma transcrição literal — antes de deixar essa evidência valer pra geração de CV (Fase 4), preciso que você confirme: era isso mesmo que você quis dizer?

### Critério de pronto — verificado
25 evidências ≥ 15 exigidas, todas rastreáveis à origem (documento ou resposta de entrevista), nenhuma inventada (exceto o ponto acima, que está sinalizado e não vai para CV sem confirmação).

## Próximo passo
Aguardar sua confirmação sobre "Camunda" e ok para começar a Fase 3 (matching TF-IDF + IA, detecção de gaps, Entrevista 2).
