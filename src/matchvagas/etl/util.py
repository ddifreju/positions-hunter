import re

_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"[ \t]+")
_BLANKLINES_RE = re.compile(r"\n{3,}")


def html_para_texto(html: str) -> str:
    """Remoção simples de tags HTML para não poluir o TF-IDF da Fase 3."""
    if not html:
        return ""
    texto = _TAG_RE.sub(" ", html)
    texto = _SPACE_RE.sub(" ", texto)
    texto = _BLANKLINES_RE.sub("\n\n", texto)
    return texto.strip()
