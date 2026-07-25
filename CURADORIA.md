# Curadoria de repositórios — MatchVagas

Avaliação dos candidatos indicados na Seção 5 do briefing. Nomes foram passados de memória; busquei cada um para confirmar existência e dados atuais (via API do GitHub, em 2026-07-25).

## awesome-claude-code

- URL: https://github.com/hesreallyhim/awesome-claude-code
- Último commit: 2026-07-25 (ativo)
- Licença: presente no repositório (lista, não código executável)
- Estrelas: ~50.9k
- O que faz (2 linhas): índice curado de recursos para Claude Code — skills, hooks, slash commands, plugins, ferramentas de terceiros. É um diretório de descoberta, não uma ferramenta instalável.
- Aplicação neste projeto: nenhuma
- Justificativa: não é algo que se "adota" no código — é uma lista para consultar pontualmente quando eu precisar achar uma skill/plugin específico. Não economiza nada por si só.
- Recomendação: descartar (usar como referência de busca quando necessário, fora do ciclo formal de adoção)

## superpowers

- URL: https://github.com/obra/superpowers
- Último commit: 2026-07-24 (ativo)
- Licença: MIT
- Estrelas: ~261k
- O que faz (2 linhas): framework de skills e metodologia de desenvolvimento agentic (brainstorming, planejamento, TDD, subagent-driven development) para Claude Code.
- Aplicação neste projeto: média
- Justificativa: o briefing já define um protocolo de trabalho específico (Seção 4.4: spec → delega → validador → integra → arquiteto revisa por fase). Adotar o framework inteiro agora duplicaria/conflitaria com esse processo já definido. Skills pontuais dele (ex.: `writing-plans`) podem valer a pena se surgir uma fricção concreta de planejamento, mas isso ainda não aconteceu.
- Recomendação: adotar depois (reavaliar skills específicas, não o framework inteiro, se uma fase futura mostrar necessidade concreta)

## claude-code-repos-index

- URL: não localizado com esse nome exato
- Candidatos próximos encontrados (nenhum é uma correspondência exata):
  - `danielrosehill/Claude-Code-Projects-Index` (517 estrelas, push em 2026-05-13) — índice pessoal de templates de projetos do autor, não um índice geral da comunidade.
  - `ericbuess/claude-code-project-index` (195 estrelas, push em 2025-09-16) — ferramenta de indexação de *código* (gera `PROJECT_INDEX.json` com funções/classes do seu repo), não um índice de *outros repositórios*.
- O que faz: nenhum dos dois candidatos corresponde à descrição de "índice de repositórios da comunidade" que o nome sugere.
- Aplicação neste projeto: nenhuma
- Justificativa: nome impreciso na memória de quem indicou; não force adoção de algo que não é o que foi pedido.
- Recomendação: descartar (não localizado)

## anthropic-skills (anthropics/skills)

- URL: https://github.com/anthropics/skills
- Último commit: 2026-07-24 (ativo)
- Licença: Apache 2.0 para a maioria das skills; as skills de criação de documentos (docx, pdf, pptx, xlsx) são source-available, não open source
- Estrelas: ~164k
- O que faz (2 linhas): repositório oficial da Anthropic com skills prontas (docx, pdf, pptx, xlsx, mcp-builder, etc.), cada uma uma pasta autocontida com instruções que o Claude carrega dinamicamente.
- Aplicação neste projeto: alta
- Justificativa: a Fase 4 (geração de CV) precisa produzir um `.docx` bem formatado a partir de dados estruturados. A skill oficial `docx` (**já disponível neste ambiente**, listada como `anthropic-skills:docx`) resolve exatamente essa parte sem eu precisar escrever lógica de geração de Word do zero — só preciso montar o conteúdo a partir do banco de evidências e invocar a skill na hora de gerar o arquivo.
- Recomendação: **adotar agora** — custo de integração é essencialmente zero (a skill já está instalada neste ambiente Claude Code, não requer nenhuma conta, chave ou instalação extra). Uso ficaria restrito à Fase 4.

## "Plugins e skills em geral"

Item genérico demais para avaliar como um repositório único — não há um nome ou URL concreto para verificar. Vou tratar isso como parte da curadoria contínua (Seção 5.4): se uma necessidade específica aparecer numa fase futura (ex.: uma skill de leitura de PDF melhor que a biblioteca padrão), avalio o candidato concreto naquele momento, sem abrir uma rodada de busca aberta agora.

---

## Recomendações "adotar agora" (bloco para aprovação)

| Item | Custo de integração estimado | O que resolve |
|---|---|---|
| `anthropic-skills:docx` (já instalada) | Zero — nenhuma conta, chave ou instalação | Geração do arquivo `.docx` do CV na Fase 4, a partir do conteúdo que o `construtor` montar do banco de evidências |

Isso respeita o limite de 2 adoções por fase (é a única nesta rodada). Aguardando seu ok para considerar `anthropic-skills:docx` adotada — até lá, ela fica só registrada aqui, sem uso no código.
