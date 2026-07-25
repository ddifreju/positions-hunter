"""Entrevistas guiadas por IA (Seção 1.2 do briefing).

Rodada 1 (intenção): 5-6 perguntas abertas para descobrir pra onde a
usuária quer ir, feitas uma vez, antes da busca de vagas.

Rodada 2 (dirigida por vagas) é implementada na Fase 3, depois que o
sistema já sabe o que o mercado está pedindo — perguntar antes disso é
chutar (Seção 7.2).
"""

from datetime import datetime, timezone

from matchvagas.db import get_client
from matchvagas.evidencias import PROMPT_EXTRACAO, parse_json_array
from matchvagas.ia import gerar

PROMPT_PERGUNTAS_INTENCAO = """\
Você vai entrevistar uma pessoa para entender para onde ela quer levar \
a carreira — não apenas de onde ela veio. Com base no resumo do \
histórico profissional abaixo, gere de 5 a 6 perguntas abertas sobre \
intenção: que tipo de vaga ela busca, que tipo de trabalho a energiza, \
o que ela quer evitar, qual o próximo passo que faz sentido para ela.

Não faça perguntas sobre fatos que já estão no resumo (isso já está \
documentado) — pergunte sobre direção, preferência e intenção futura.

Devolva APENAS um array JSON de strings, sem texto antes ou depois:
["pergunta 1", "pergunta 2", ...]

Resumo do histórico:
---
{resumo}
---
"""


def gerar_perguntas_intencao(usuaria_id: str, resumo: str) -> list[dict]:
    resposta = gerar(PROMPT_PERGUNTAS_INTENCAO.format(resumo=resumo), tarefa="entrevista_perguntas")
    perguntas_texto = parse_json_array(resposta)

    linhas = [
        {"usuaria_id": usuaria_id, "rodada": 1, "texto": p}
        for p in perguntas_texto
        if p and p.strip()
    ]
    client = get_client(admin=True)
    inserido = client.table("perguntas").insert(linhas).execute()
    return inserido.data


def registrar_resposta(pergunta_id: str, resposta_texto: str) -> dict:
    client = get_client(admin=True)
    pergunta = client.table("perguntas").select("*").eq("id", pergunta_id).execute().data[0]

    prompt_evidencia = PROMPT_EXTRACAO.format(
        texto=f"Pergunta: {pergunta['texto']}\nResposta: {resposta_texto}"
    )
    resposta_ia = gerar(prompt_evidencia, tarefa="extracao_pdf")
    itens = parse_json_array(resposta_ia)

    evidencia_id = None
    if itens:
        evidencia = (
            client.table("evidencias")
            .insert(
                {
                    "usuaria_id": pergunta["usuaria_id"],
                    "texto": itens[0]["texto"],
                    "tags": itens[0].get("tags", []),
                    "fonte": "entrevista",
                }
            )
            .execute()
        )
        evidencia_id = evidencia.data[0]["id"]

    atualizado = (
        client.table("perguntas")
        .update(
            {
                "resposta": resposta_texto,
                "respondida_em": datetime.now(timezone.utc).isoformat(),
                "gerou_evidencia_id": evidencia_id,
            }
        )
        .eq("id", pergunta_id)
        .execute()
    )
    return atualizado.data[0]
