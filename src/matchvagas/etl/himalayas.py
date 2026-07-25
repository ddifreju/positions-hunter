"""Fonte: Himalayas (https://himalayas.app/jobs/api). Sem chave.

Paginado por offset, 20 vagas fixas por página (o parâmetro `limit` é
ignorado pela API). totalCount passa de 90 mil — limitamos páginas por
padrão, não há volume de usuárias que justifique baixar tudo.
"""

import requests

from .util import html_para_texto

URL = "https://himalayas.app/jobs/api"
TAMANHO_PAGINA = 20


def coletar(max_paginas: int = 5) -> list[dict]:
    vagas = []
    for pagina in range(max_paginas):
        offset = pagina * TAMANHO_PAGINA
        resposta = requests.get(
            URL,
            params={"limit": TAMANHO_PAGINA, "offset": offset},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30,
        )
        resposta.raise_for_status()
        jobs = resposta.json().get("jobs", [])
        if not jobs:
            break
        for job in jobs:
            localizacoes = job.get("locationRestrictions") or []
            vagas.append(
                {
                    "plataforma": "himalayas",
                    "id_externo": job["guid"],
                    "titulo": job.get("title"),
                    "empresa": job.get("companyName"),
                    "descricao": html_para_texto(job.get("description", "")),
                    "url_candidatura": job.get("applicationLink") or job.get("guid"),
                    "modalidade": "remoto",
                    "localizacao": ", ".join(localizacoes) if localizacoes else None,
                }
            )
    return vagas
