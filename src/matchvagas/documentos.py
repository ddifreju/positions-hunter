"""Upload e extração de texto de documentos da usuária (Fase 2).

Nada persiste em disco local além do arquivo temporário de origem que a
própria interface (ou o script de teste) já tem em mãos — o texto e o
arquivo em si vão para o Supabase (Storage + tabela `documentos`).
"""

import uuid
from pathlib import Path

from pypdf import PdfReader

from matchvagas.db import get_client

BUCKET = "documentos"
TIPOS_VALIDOS = {"cv", "linkedin", "certificado", "portfolio", "outro"}


def extrair_texto_pdf(caminho: str) -> str:
    leitor = PdfReader(caminho)
    paginas = [pagina.extract_text() or "" for pagina in leitor.pages]
    return "\n\n".join(paginas).strip()


def enviar_documento(usuaria_id: str, caminho: str, tipo: str) -> dict:
    if tipo not in TIPOS_VALIDOS:
        raise ValueError(f"tipo inválido: {tipo!r} (esperado um de {TIPOS_VALIDOS})")

    texto = extrair_texto_pdf(caminho)
    if not texto:
        raise ValueError(f"não foi possível extrair texto de {caminho}")

    nome_arquivo = Path(caminho).name
    storage_path = f"{usuaria_id}/{uuid.uuid4()}_{nome_arquivo}"

    client = get_client(admin=True)
    with open(caminho, "rb") as f:
        client.storage.from_(BUCKET).upload(
            storage_path, f.read(), file_options={"content-type": "application/pdf"}
        )

    inserido = (
        client.table("documentos")
        .insert(
            {
                "usuaria_id": usuaria_id,
                "tipo": tipo,
                "nome_arquivo": nome_arquivo,
                "storage_path": storage_path,
                "texto_extraido": texto,
            }
        )
        .execute()
    )
    return inserido.data[0]
