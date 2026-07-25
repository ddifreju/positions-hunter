"""Critério de pronto da Fase 0: ler e escrever no Supabase.

Requer SUPABASE_URL e SUPABASE_SERVICE_KEY em .env. Cria uma usuária de
teste, lê de volta e apaga em seguida.
"""

from dotenv import load_dotenv

from matchvagas.db import get_client

load_dotenv()


def test_escreve_e_le_usuaria():
    client = get_client(admin=True)

    inserida = client.table("usuarias").insert({"nome": "_teste_conexao"}).execute()
    usuaria_id = inserida.data[0]["id"]

    lida = client.table("usuarias").select("*").eq("id", usuaria_id).execute()
    assert lida.data[0]["nome"] == "_teste_conexao"

    client.table("usuarias").delete().eq("id", usuaria_id).execute()
