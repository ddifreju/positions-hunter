"""Fonte: Remotive (https://remotive.com/api/remote-jobs). Sem chave."""

import requests

from .util import html_para_texto

URL = "https://remotive.com/api/remote-jobs"


def coletar() -> list[dict]:
    resposta = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resposta.raise_for_status()
    vagas = []
    for job in resposta.json()["jobs"]:
        vagas.append(
            {
                "plataforma": "remotive",
                "id_externo": str(job["id"]),
                "titulo": job.get("title"),
                "empresa": job.get("company_name"),
                "descricao": html_para_texto(job.get("description", "")),
                "url_candidatura": job.get("url"),
                "modalidade": "remoto",
                "localizacao": job.get("candidate_required_location"),
            }
        )
    return vagas
