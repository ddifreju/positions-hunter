# MatchVagas

Gestor de candidaturas que aprende com cada vaga: extrai evidências reais de currículo/LinkedIn/portfólio, descobre os buracos entre o que o mercado pede e o que está documentado, e gera currículos customizados **usando apenas evidências reais** — nunca inventa experiência, número, empresa, cargo ou habilidade.

Construído para duas usuárias, a custo zero.

## Stack

| Camada | Escolha |
|---|---|
| Frontend | Streamlit multipage |
| Banco | Supabase (Postgres) |
| Arquivos | Supabase Storage |
| Agendamento | GitHub Actions (cron diário) |
| IA | Gemini Flash (padrão) + fallback via `gerar()`, Ollama para tarefas locais |
| Linguagem | Python 3.11+ |

## Setup local

```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
cp .env.example .env  # preencher com as chaves reais
```

Variáveis necessárias em `.env`: ver `.env.example`.

## Rodar

```bash
streamlit run app/Home.py
```

## Estrutura

```
app/            páginas Streamlit (Perfil, Vagas, Candidaturas, Estudo, Evolução)
src/            lógica: ia (gerar()), banco, ETL de vagas, evidências, matching, geração de CV
sql/schema.sql  schema do Supabase
tests/          testes automatizados (inclui o teste obrigatório da regra R2)
.claude/agents/ agentes do time (arquiteto, construtor, validador)
```

## Regras invioláveis do projeto

1. **Custo zero.** Nenhum serviço pago sem autorização explícita.
2. **Nunca inventar currículo.** O gerador só seleciona, reordena e reescreve evidências reais do banco.
3. **Nada de scraping de LinkedIn** nem automação de Easy Apply. Entrada de perfil é via PDF exportado.
4. **Segredos só em `.env`/Secrets do CI**, nunca no código.
5. **Dado pessoal é sensível** (LGPD) — banco privado enquanto houver só usuárias conhecidas.

Detalhes completos no briefing do projeto (`BRIEFING_AGENTE_MATCHVAGAS.md`, mantido fora do repositório).

## Acompanhamento

- `PROGRESSO.md` — o que foi feito, o que quebrou, o que está pendente.
- `EQUIPE.md` — agentes ativos e justificativa de cada um.
- `CURADORIA.md` — repositórios/ferramentas avaliados para adoção.
- `DEBITO_TECNICO.md` — problemas conhecidos registrados para revisão futura, não corrigidos no calor da fase atual.
