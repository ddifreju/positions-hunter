"""Geração do banco de evidências a partir de documentos (Fase 2).

R2 é aplicada aqui na origem: o prompt proíbe explicitamente inventar
qualquer realização, número, empresa, cargo ou habilidade que não
esteja no texto de entrada. Cada evidência extraída é uma frase que
precisa existir, em substância, no documento de origem.
"""

import json
import re

from matchvagas.db import get_client
from matchvagas.ia import gerar

PROMPT_EXTRACAO = """\
Você extrai evidências de um currículo/perfil profissional para um banco \
de dados. Uma evidência é uma realização, responsabilidade ou habilidade \
concreta e verificável.

REGRA ABSOLUTA: você só pode extrair o que está literalmente escrito ou \
diretamente implícito no texto abaixo. NUNCA invente empresa, cargo, \
número, prazo, ferramenta ou habilidade que não apareça no texto. Se o \
texto for vago, a evidência extraída também deve ser vaga — não \
complete a lacuna com suposição.

Devolva APENAS um array JSON, sem texto antes ou depois, no formato:
[{{"texto": "frase da evidência", "tags": ["tag1", "tag2"]}}, ...]

`tags` são palavras-chave de habilidade/tecnologia/domínio associadas à \
evidência (minúsculas, sem acento quando possível).

Texto de origem:
---
{texto}
---
"""


def parse_json_array(resposta: str) -> list:
    limpo = re.sub(r"^```(json)?|```$", "", resposta.strip(), flags=re.MULTILINE).strip()
    dados = json.loads(limpo)
    if not isinstance(dados, list):
        raise ValueError("resposta do modelo não é uma lista JSON")
    return dados


def gerar_evidencias_do_documento(usuaria_id: str, documento_id: str, texto: str) -> list[dict]:
    resposta = gerar(PROMPT_EXTRACAO.format(texto=texto), tarefa="extracao_pdf")
    itens = parse_json_array(resposta)

    linhas = [
        {
            "usuaria_id": usuaria_id,
            "texto": item["texto"],
            "tags": item.get("tags", []),
            "fonte": "documento",
            "documento_id": documento_id,
        }
        for item in itens
        if item.get("texto")
    ]
    if not linhas:
        return []

    client = get_client(admin=True)
    inserido = client.table("evidencias").insert(linhas).execute()
    return inserido.data


def resumo_evidencias(usuaria_id: str) -> str:
    """Junta as evidências já registradas num texto único, usado como
    contexto para gerar as perguntas da Entrevista 1."""
    client = get_client(admin=True)
    linhas = (
        client.table("evidencias").select("texto,tags").eq("usuaria_id", usuaria_id).execute().data
    )
    return "\n".join(f"- {linha['texto']} (tags: {', '.join(linha['tags'])})" for linha in linhas)
