"""Fonte: RemoteOK (https://remoteok.com/api). Sem chave.

O primeiro item da lista é um aviso legal, não uma vaga — precisa ser
descartado.
"""

import requests

from .util import html_para_texto

URL = "https://remoteok.com/api"


def coletar() -> list[dict]:
    resposta = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resposta.raise_for_status()
    jobs = resposta.json()[1:]
    vagas = []
    for job in jobs:
        vagas.append(
            {
                "plataforma": "remoteok",
                "id_externo": str(job["id"]),
                "titulo": job.get("position"),
                "empresa": job.get("company"),
                "descricao": html_para_texto(job.get("description", "")),
                "url_candidatura": job.get("apply_url") or job.get("url"),
                "modalidade": "remoto",
                "localizacao": job.get("location"),
            }
        )
    return vagas
