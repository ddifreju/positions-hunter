"""Fonte: We Work Remotely (RSS). Sem chave.

O título vem no formato "Empresa: Cargo" — separamos no primeiro ":".
Quando não segue o padrão, usamos o título inteiro e deixamos empresa
em branco em vez de adivinhar.
"""

import feedparser

from .util import html_para_texto

URL = "https://weworkremotely.com/remote-jobs.rss"


def coletar() -> list[dict]:
    feed = feedparser.parse(URL)
    vagas = []
    for entrada in feed.entries:
        titulo_bruto = entrada.get("title", "")
        if ": " in titulo_bruto:
            empresa, titulo = titulo_bruto.split(": ", 1)
        else:
            empresa, titulo = None, titulo_bruto

        vagas.append(
            {
                "plataforma": "weworkremotely",
                "id_externo": entrada.get("id") or entrada.get("link"),
                "titulo": titulo,
                "empresa": empresa,
                "descricao": html_para_texto(entrada.get("summary", "")),
                "url_candidatura": entrada.get("link"),
                "modalidade": "remoto",
                "localizacao": entrada.get("region"),
            }
        )
    return vagas
