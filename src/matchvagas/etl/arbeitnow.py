"""Fonte: Arbeitnow (https://www.arbeitnow.com/api/job-board-api). Sem chave.

Paginado (100 vagas por página). Limitamos o número de páginas por
padrão — não há volume de usuárias que justifique baixar tudo.
"""

import requests

from .util import html_para_texto

URL = "https://www.arbeitnow.com/api/job-board-api"


def coletar(max_paginas: int = 3) -> list[dict]:
    vagas = []
    url = URL
    paginas = 0
    while url and paginas < max_paginas:
        resposta = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        resposta.raise_for_status()
        corpo = resposta.json()
        for job in corpo["data"]:
            vagas.append(
                {
                    "plataforma": "arbeitnow",
                    "id_externo": job["slug"],
                    "titulo": job.get("title"),
                    "empresa": job.get("company_name"),
                    "descricao": html_para_texto(job.get("description", "")),
                    "url_candidatura": job.get("url"),
                    "modalidade": "remoto" if job.get("remote") else None,
                    "localizacao": job.get("location"),
                }
            )
        url = corpo.get("links", {}).get("next")
        paginas += 1
    return vagas
