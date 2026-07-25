"""Ponto único de acesso a modelos de IA (Seção 6.1 do briefing).

Nenhum outro módulo deve chamar API de modelo diretamente. Quando um
provedor mudar as regras do free tier, a troca é só aqui.
"""

import os

# Roteamento por tarefa: cada tarefa tem uma lista de provedores tentados
# em ordem (fallback automático). "melhor" = o modelo de maior qualidade
# disponível no momento, reservado para o produto final (Seção 6.2).
ROTEAMENTO = {
    "extracao_pdf": ["gemini", "groq"],
    "entrevista_perguntas": ["gemini", "groq"],
    "classificacao_gap": ["groq", "gemini"],
    "cv_geracao": ["gemini", "groq"],
}

MODELOS = {
    "gemini": "gemini-2.5-flash",
    "groq": "llama-3.3-70b-versatile",
}


def _chamar_gemini(prompt: str) -> str:
    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resposta = client.models.generate_content(model=MODELOS["gemini"], contents=prompt)
    return resposta.text


def _chamar_groq(prompt: str) -> str:
    from groq import Groq

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resposta = client.chat.completions.create(
        model=MODELOS["groq"],
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
    provedores = ROTEAMENTO.get(tarefa)
    if not provedores:
        raise ValueError(f"tarefa desconhecida: {tarefa!r}")

    erros = []
    for provedor in provedores:
        try:
            return CHAMADORES[provedor](prompt)
        except Exception as e:
            erros.append(f"{provedor}: {e}")

    raise RuntimeError(
        f"todos os provedores falharam para a tarefa {tarefa!r}: {'; '.join(erros)}"
    )
