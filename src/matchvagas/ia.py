"""Ponto único de acesso a modelos de IA (Seção 6.1 do briefing).

Nenhum outro módulo deve chamar API de modelo diretamente. Quando um
provedor mudar as regras do free tier, a troca é só aqui.
"""

import os

# Roteamento por tarefa: cada tarefa tem uma lista de (provedor, modelo)
# tentados em ordem (fallback automático). Modelos "-latest" do Gemini
# apontam sempre para a versão atual — evita quebrar quando um nome de
# modelo fixo é descontinuado (Seção 6.3: valide sempre na documentação
# oficial, não confie em memória de treino).
ROTEAMENTO = {
    "extracao_pdf": [("gemini", "gemini-flash-latest"), ("groq", "llama-3.3-70b-versatile")],
    "entrevista_perguntas": [("gemini", "gemini-flash-latest"), ("groq", "llama-3.3-70b-versatile")],
    "classificacao_gap": [("groq", "llama-3.3-70b-versatile"), ("gemini", "gemini-flash-latest")],
    "cv_geracao": [("gemini", "gemini-pro-latest"), ("groq", "llama-3.3-70b-versatile")],
}


def _chamar_gemini(prompt: str, modelo: str) -> str:
    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resposta = client.models.generate_content(model=modelo, contents=prompt)
    return resposta.text


def _chamar_groq(prompt: str, modelo: str) -> str:
    from groq import Groq

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resposta = client.chat.completions.create(
        model=modelo,
        messages=[{"role": "user", "content": prompt}],
    )
    return resposta.choices[0].message.content


CHAMADORES = {
    "gemini": _chamar_gemini,
    "groq": _chamar_groq,
}


def gerar(prompt: str, tarefa: str) -> str:
    """Gera texto para `tarefa`, tentando os provedores da tabela de
    roteamento em ordem até um responder.
    """
    rota = ROTEAMENTO.get(tarefa)
    if not rota:
        raise ValueError(f"tarefa desconhecida: {tarefa!r}")

    erros = []
    for provedor, modelo in rota:
        try:
            return CHAMADORES[provedor](prompt, modelo)
        except Exception as e:
            erros.append(f"{provedor}/{modelo}: {e}")

    raise RuntimeError(
        f"todos os provedores falharam para a tarefa {tarefa!r}: {'; '.join(erros)}"
    )
