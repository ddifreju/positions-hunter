"""Smoke test da Entrevista 1 (intenção): gera perguntas a partir de um
resumo sintético, registra uma resposta e confirma que vira evidência.
"""

from dotenv import load_dotenv

from matchvagas.db import get_client
from matchvagas.entrevista import gerar_perguntas_intencao, registrar_resposta

load_dotenv()

RESUMO_FAKE = (
    "- Liderou migração de pipeline de ETL de Python 2 para Python 3 "
    "(tags: python, etl)\n"
    "- Construiu dashboard em Power BI usado por 3 times de negócio "
    "(tags: powerbi, dados)"
)


def test_gera_perguntas_e_registra_resposta():
    client = get_client(admin=True)
    usuaria = client.table("usuarias").insert({"nome": "_teste_entrevista"}).execute().data[0]
    usuaria_id = usuaria["id"]

    try:
        perguntas = gerar_perguntas_intencao(usuaria_id, RESUMO_FAKE)
        assert 3 <= len(perguntas) <= 8
        for p in perguntas:
            assert p["rodada"] == 1
            assert p["texto"]

        primeira = perguntas[0]
        atualizada = registrar_resposta(
            primeira["id"], "Quero migrar para uma vaga de engenharia de dados sênior."
        )
        assert atualizada["resposta"]
        assert atualizada["respondida_em"]
    finally:
        client.table("usuarias").delete().eq("id", usuaria_id).execute()
