"""Orquestra a coleta de todas as fontes e grava na tabela `vagas`.

Uma fonte que falhar não derruba as outras — só é registrada como erro
(Fase 1: "descartar as que não responderem").
"""

from matchvagas.db import get_client

from . import arbeitnow, himalayas, remoteok, remotive, weworkremotely

FONTES = {
    "remotive": remotive.coletar,
    "remoteok": remoteok.coletar,
    "arbeitnow": arbeitnow.coletar,
    "himalayas": himalayas.coletar,
    "weworkremotely": weworkremotely.coletar,
}


def coletar_todas() -> tuple[list[dict], dict[str, str]]:
    por_chave: dict[tuple[str, str], dict] = {}
    erros = {}
    for nome, coletor in FONTES.items():
        try:
            colhidas = coletor()
            for v in colhidas:
                if not v.get("id_externo"):
                    continue
                # a própria fonte às vezes repete a mesma vaga na paginação;
                # a última ocorrência vence.
                por_chave[(v["plataforma"], v["id_externo"])] = v
        except Exception as e:
            erros[nome] = str(e)
    return list(por_chave.values()), erros


def gravar(vagas: list[dict], tamanho_lote: int = 500) -> int:
    if not vagas:
        return 0
    client = get_client(admin=True)
    gravadas = 0
    for i in range(0, len(vagas), tamanho_lote):
        lote = vagas[i : i + tamanho_lote]
        client.table("vagas").upsert(lote, on_conflict="plataforma,id_externo").execute()
        gravadas += len(lote)
    return gravadas


def rodar() -> None:
    vagas, erros = coletar_todas()
    print(f"coletadas {len(vagas)} vagas de {len(FONTES) - len(erros)}/{len(FONTES)} fontes")
    for nome, erro in erros.items():
        print(f"  fonte descartada nesta rodada — {nome}: {erro}")
    gravadas = gravar(vagas)
    print(f"gravadas/atualizadas {gravadas} vagas no Supabase")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    rodar()
