"""Parsing das respostas em JSON que os prompts de `gerar()` pedem."""

import json
import re


def _limpar_cercas_markdown(texto: str) -> str:
    return re.sub(r"^```(json)?|```$", "", texto.strip(), flags=re.MULTILINE).strip()


def parse_json(texto: str):
    return json.loads(_limpar_cercas_markdown(texto))


def parse_json_array(texto: str) -> list:
    dados = parse_json(texto)
    if not isinstance(dados, list):
        raise ValueError("resposta do modelo não é uma lista JSON")
    return dados
