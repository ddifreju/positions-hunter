"""Smoke test do pipeline de documento -> evidências (Fase 2), com um
PDF sintético (não é currículo real de ninguém). Confirma que a
mecânica funciona: upload, extração, geração de evidências via IA e
que cada evidência tem lastro no texto de origem — não substitui o
critério de pronto real da fase, que exige o CV de uma usuária de
verdade.
"""

import io

from dotenv import load_dotenv
from reportlab.pdfgen import canvas

from matchvagas.db import get_client
from matchvagas.documentos import enviar_documento
from matchvagas.evidencias import gerar_evidencias_do_documento

load_dotenv()

CONTEUDO_FAKE = [
    "Maria Teste — Analista de Dados",
    "Liderou migração de pipeline de ETL de Python 2 para Python 3,",
    "reduzindo o tempo de processamento diário em 40%.",
    "Construiu dashboard em Power BI usado por 3 times de negócio.",
    "Certificação AWS Cloud Practitioner, obtida em 2024.",
    "Ensinou SQL avançado para 8 estagiários ao longo de 2023.",
]


def _criar_pdf_sintetico(caminho: str) -> None:
    c = canvas.Canvas(caminho)
    y = 800
    for linha in CONTEUDO_FAKE:
        c.drawString(50, y, linha)
        y -= 20
    c.save()


def test_pipeline_documento_para_evidencias(tmp_path):
    client = get_client(admin=True)
    usuaria = client.table("usuarias").insert({"nome": "_teste_evidencias"}).execute().data[0]
    usuaria_id = usuaria["id"]

    caminho_pdf = tmp_path / "cv_fake.pdf"
    _criar_pdf_sintetico(str(caminho_pdf))

    documento = None
    try:
        documento = enviar_documento(usuaria_id, str(caminho_pdf), tipo="cv")
        assert documento["texto_extraido"]
        assert "Power BI" in documento["texto_extraido"]

        evidencias = gerar_evidencias_do_documento(
            usuaria_id, documento["id"], documento["texto_extraido"]
        )
        assert len(evidencias) >= 1
        for ev in evidencias:
            assert ev["fonte"] == "documento"
            assert ev["texto"]
    finally:
        if documento is not None:
            client.storage.from_("documentos").remove([documento["storage_path"]])
        client.table("usuarias").delete().eq("id", usuaria_id).execute()
