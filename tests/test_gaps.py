"""Smoke test da classificação e do acúmulo de frequência de gaps
(Seção 7.4). Usa dado sintético — não testa a qualidade da
classificação em si (isso é sensível ao modelo), só a mecânica.
"""

from dotenv import load_dotenv

from matchvagas.db import get_client
from matchvagas.gaps import registrar_gap

load_dotenv()


def test_registrar_gap_incrementa_frequencia_em_vez_de_duplicar():
    client = get_client(admin=True)
    usuaria = client.table("usuarias").insert({"nome": "_teste_gaps"}).execute().data[0]
    usuaria_id = usuaria["id"]

    try:
        primeiro = registrar_gap(usuaria_id, "Terraform")
        assert primeiro["frequencia"] == 1
        assert primeiro["tipo"] in ("documentacao", "competencia")
        assert primeiro["status"] == "aberto"

        segundo = registrar_gap(usuaria_id, "terraform")  # variação de caixa
        assert segundo["id"] == primeiro["id"]
        assert segundo["frequencia"] == 2
        assert segundo["tipo"] == primeiro["tipo"]  # não reclassifica

        todos = client.table("gaps").select("id").eq("usuaria_id", usuaria_id).execute().data
        assert len(todos) == 1
    finally:
        client.table("usuarias").delete().eq("id", usuaria_id).execute()
