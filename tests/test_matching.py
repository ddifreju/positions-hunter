"""Smoke test da camada 1 (TF-IDF, sem IA): confirma que uma vaga
claramente relacionada ao perfil pontua mais alto que uma vaga sem
nenhuma relação, usando dado sintético contra o Supabase real.
"""

from dotenv import load_dotenv

from matchvagas.db import get_client
from matchvagas.matching import camada1_tfidf

load_dotenv()


def test_vaga_relacionada_pontua_mais_que_vaga_nao_relacionada():
    client = get_client(admin=True)
    usuaria = client.table("usuarias").insert({"nome": "_teste_matching"}).execute().data[0]
    usuaria_id = usuaria["id"]

    client.table("evidencias").insert(
        {
            "usuaria_id": usuaria_id,
            "texto": "Desenvolvimento de pipelines de dados em Python com SQL e machine learning",
            "tags": ["python", "sql", "machine learning"],
            "fonte": "documento",
        }
    ).execute()

    vaga_relacionada = (
        client.table("vagas")
        .insert(
            {
                "plataforma": "_teste",
                "id_externo": "_teste_relacionada",
                "titulo": "Engenheira de Dados Python",
                "descricao": "Procuramos experiência em Python, SQL e machine learning para pipelines de dados.",
            }
        )
        .execute()
        .data[0]
    )
    vaga_nao_relacionada = (
        client.table("vagas")
        .insert(
            {
                "plataforma": "_teste",
                "id_externo": "_teste_nao_relacionada",
                "titulo": "Confeiteira",
                "descricao": "Procuramos profissional para produção de bolos e doces em confeitaria artesanal.",
            }
        )
        .execute()
        .data[0]
    )

    try:
        # top_n grande o bastante pra cobrir todas as vagas reais já
        # coletadas na Fase 1 — o que importa aqui é comparar as duas
        # vagas sintéticas entre si, não o corte do top N.
        resultado = camada1_tfidf(usuaria_id, top_n=100_000)
        scores = {r["vaga"]["id_externo"]: r["score_tfidf"] for r in resultado}
        assert scores["_teste_relacionada"] > scores["_teste_nao_relacionada"]
    finally:
        client.table("vagas").delete().eq("id", vaga_relacionada["id"]).execute()
        client.table("vagas").delete().eq("id", vaga_nao_relacionada["id"]).execute()
        client.table("usuarias").delete().eq("id", usuaria_id).execute()
