"""Checa se cada fonte de vaga da Fase 1 ainda responde e devolve dados
no formato esperado pela tabela `vagas`. Papel do `validador`: rodar
isso periodicamente e reportar fontes que pararam de responder.
"""

import pytest

from matchvagas.etl import arbeitnow, himalayas, remoteok, remotive, weworkremotely

CAMPOS_OBRIGATORIOS = {"plataforma", "id_externo", "titulo", "url_candidatura"}

FONTES = {
    "remotive": remotive.coletar,
    "remoteok": remoteok.coletar,
    "arbeitnow": arbeitnow.coletar,
    "himalayas": himalayas.coletar,
    "weworkremotely": weworkremotely.coletar,
}


@pytest.mark.parametrize("nome,coletor", FONTES.items())
def test_fonte_responde_e_normaliza(nome, coletor):
    vagas = coletor()
    assert len(vagas) > 0, f"{nome} não retornou nenhuma vaga"

    primeira = vagas[0]
    faltando = CAMPOS_OBRIGATORIOS - primeira.keys()
    assert not faltando, f"{nome}: campos ausentes {faltando}"
    assert primeira["plataforma"] == nome
    assert primeira["id_externo"]
    assert primeira["titulo"]


def test_runner_deduplica_antes_de_gravar():
    """Algumas fontes paginadas (ex.: Himalayas) podem repetir um item
    entre páginas quando o catálogo muda durante a coleta. Isso não é
    bug da fonte — o que importa é que o runner nunca produza duas
    linhas com a mesma (plataforma, id_externo), já que essa é a chave
    única da tabela `vagas`.
    """
    from matchvagas.etl.runner import coletar_todas

    vagas, _ = coletar_todas()
    chaves = [(v["plataforma"], v["id_externo"]) for v in vagas]
    assert len(chaves) == len(set(chaves))
