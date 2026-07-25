"""Critério de pronto da Fase 0: gerar() responde por dois provedores.

Requer GEMINI_API_KEY e GROQ_API_KEY em .env.
"""

from dotenv import load_dotenv

from matchvagas.ia import _chamar_gemini, _chamar_groq

load_dotenv()

PROMPT = "Responda apenas com a palavra: ok"


def test_gemini_responde():
    assert len(_chamar_gemini(PROMPT, "gemini-flash-latest").strip()) > 0


def test_groq_responde():
    assert len(_chamar_groq(PROMPT, "llama-3.3-70b-versatile").strip()) > 0
