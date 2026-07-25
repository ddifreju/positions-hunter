"""Detecção e classificação de gaps (Seção 7.4 do briefing — o coração
do produto).

Confundir os dois tipos é o erro que inflaria o currículo: na dúvida,
classifica como "competencia" (Seção 7.4). "documentacao" só quando a
habilidade for claramente próxima de algo que já está no banco.
"""

from matchvagas.db import get_client
from matchvagas.evidencias import resumo_evidencias
from matchvagas.ia import gerar

PROMPT_CLASSIFICACAO_GAP = """\
Você decide se uma habilidade que uma vaga pede, mas que não está no \
banco de evidências da candidata, é do tipo "documentacao" ou \
"competencia".

documentacao: a pessoa provavelmente já tem essa habilidade, só não \
está escrita — a habilidade é próxima ou implícita em evidências que \
ela já tem.
competencia: não há nada no perfil que sugira que ela tem essa \
habilidade.

Na dúvida, responda competencia — é mais seguro sugerir estudo do que \
arriscar inflar o currículo com algo que ela pode não saber.

Perfil da candidata:
---
{perfil}
---

Habilidade a classificar: {skill}

Devolva APENAS uma palavra, sem mais nada: documentacao ou competencia.
"""


def classificar_gap(usuaria_id: str, skill: str) -> str:
    perfil = resumo_evidencias(usuaria_id)
    resposta = gerar(PROMPT_CLASSIFICACAO_GAP.format(perfil=perfil, skill=skill), tarefa="classificacao_gap")
    tipo = resposta.strip().lower()
    return tipo if tipo in ("documentacao", "competencia") else "competencia"


def registrar_gap(usuaria_id: str, skill: str) -> dict:
    skill_normalizada = skill.strip().lower()
    client = get_client(admin=True)

    existente = (
        client.table("gaps")
        .select("*")
        .eq("usuaria_id", usuaria_id)
        .eq("skill", skill_normalizada)
        .execute()
        .data
    )

    if existente:
        gap = existente[0]
        atualizado = (
            client.table("gaps")
            .update({"frequencia": gap["frequencia"] + 1})
            .eq("id", gap["id"])
            .execute()
        )
        return atualizado.data[0]

    tipo = classificar_gap(usuaria_id, skill_normalizada)
    inserido = (
        client.table("gaps")
        .insert({"usuaria_id": usuaria_id, "skill": skill_normalizada, "tipo": tipo, "frequencia": 1})
        .execute()
    )
    return inserido.data[0]


def processar_habilidades_faltantes(usuaria_id: str, habilidades: list[str]) -> list[dict]:
    return [registrar_gap(usuaria_id, skill) for skill in habilidades if skill and skill.strip()]
