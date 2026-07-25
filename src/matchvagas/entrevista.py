"""Entrevistas guiadas por IA (Seção 1.2 do briefing).

Rodada 1 (intenção): 5-6 perguntas simples para descobrir pra onde a
usuária quer ir, feitas uma vez, antes da busca de vagas.

Rodada 2 (dirigida por vagas) é implementada na Fase 3, depois que o
sistema já sabe o que o mercado está pedindo — perguntar antes disso é
chutar (Seção 7.2).

Duas coisas aprendidas testando com dado real: perguntas geradas direto
do jargão do resumo saem complexas demais para responder de bate-pronto;
e a resposta da pessoa (que pode vir informal, corrida, com hesitação)
não pode virar evidência ao pé da letra — precisa ser reescrita em
linguagem corporativa antes de entrar no banco, sem adicionar fato novo.
"""

from datetime import datetime, timezone

from matchvagas.db import get_client
from matchvagas.evidencias import resumo_evidencias
from matchvagas.ia import gerar
from matchvagas.parsing import parse_json_array

PROMPT_PERGUNTAS_INTENCAO = """\
Você vai entrevistar uma pessoa para entender pra onde ela quer levar a \
carreira — não repetir o que já se sabe sobre o passado dela.

Gere de 5 a 6 perguntas SIMPLES, em linguagem do dia a dia, sem jargão \
técnico ou corporativo (nada de "hands-on", "porte da empresa", \
"maturidade técnica" etc.). Uma pessoa sem vocabulário de RH precisa \
entender e responder de bate-pronto, em uma ou duas frases. Uma ideia \
por pergunta — evite perguntas com várias partes encadeadas por "e" ou \
"em relação a".

Mesmo simples, as perguntas precisam ser estratégicas: cada resposta \
deve ajudar a identificar habilidades, preferências de trabalho ou \
pontos fortes que depois serão comparados com o que vagas reais pedem.

Temas a cobrir, em linguagem simples (não copie estes termos técnicos): \
que tipo de trabalho a pessoa quer fazer no dia a dia; o que ela quer \
evitar; que tipo de ambiente combina com ela; como ela vê os próximos \
passos; o que faria ela se sentir bem-sucedida.

Com base no resumo do histórico profissional abaixo, gere as perguntas.

Devolva APENAS um array JSON de strings, sem texto antes ou depois:
["pergunta 1", "pergunta 2", ...]

Resumo do histórico:
---
{resumo}
---
"""

PROMPT_EVIDENCIA_RESPOSTA = """\
Você transforma a resposta de uma pessoa numa entrevista de carreira em \
evidência de perfil profissional, escrita em linguagem corporativa, \
clara e amigável — como apareceria num currículo bem escrito.

REGRA ABSOLUTA: use só o que a pessoa disse. Não invente ferramenta, \
empresa, número, prazo ou habilidade que não esteja na resposta. Você \
pode e deve: corrigir gramática, remover hesitação e repetição, juntar \
a ideia numa frase completa e profissional, trocar expressão informal \
por equivalente formal — mas sem acrescentar fato novo.

Se a resposta descrever uma preferência ou desejo (não uma habilidade \
já comprovada), gere a evidência mesmo assim, mas deixando claro que é \
preferência, não fato comprovado (ex.: "Busca ambiente colaborativo e \
com autonomia de trabalho", não "Tem experiência em ambiente \
colaborativo").

Se a resposta não tiver nenhum conteúdo aproveitável como evidência de \
perfil, devolva uma lista vazia. Uma resposta rica pode gerar mais de \
uma evidência.

Devolva APENAS um array JSON, sem texto antes ou depois, no formato:
[{{"texto": "frase da evidência em linguagem corporativa", "tags": ["tag1"]}}]

Pergunta: {pergunta}
Resposta da pessoa: {resposta}
"""

PROMPT_PERGUNTA_GAP = """\
Uma vaga real pede a habilidade "{skill}", que não está registrada no \
perfil da candidata — mas o perfil dela sugere que ela provavelmente \
já tem essa habilidade, só não documentou.

Escreva UMA pergunta simples, em linguagem do dia a dia, sem jargão, \
que confirme se ela já fez algo relacionado a "{skill}" — mesmo que \
informal ou em outro contexto. A pessoa precisa entender e responder \
em uma frase, sem precisar pensar muito.

Perfil da candidata:
---
{perfil}
---

Devolva APENAS a pergunta, sem mais nada, sem aspas.
"""


def gerar_perguntas_gaps(usuaria_id: str) -> list[dict]:
    """Entrevista 2: uma pergunta por gap tipo "documentacao" ainda em
    aberto, dirigida pelo que as vagas de verdade estão pedindo (Seção
    7.2) — nunca repete pergunta já feita para essa usuária."""
    client = get_client(admin=True)
    gaps = (
        client.table("gaps")
        .select("*")
        .eq("usuaria_id", usuaria_id)
        .eq("tipo", "documentacao")
        .eq("status", "aberto")
        .execute()
        .data
    )
    if not gaps:
        return []

    ja_perguntado = {
        p["texto"]
        for p in client.table("perguntas").select("texto").eq("usuaria_id", usuaria_id).execute().data
    }

    perfil = resumo_evidencias(usuaria_id)
    linhas = []
    for gap in gaps:
        texto = gerar(
            PROMPT_PERGUNTA_GAP.format(skill=gap["skill"], perfil=perfil), tarefa="entrevista_perguntas"
        ).strip()
        if texto and texto not in ja_perguntado:
            linhas.append({"usuaria_id": usuaria_id, "rodada": 2, "texto": texto, "gap_id": gap["id"]})
            ja_perguntado.add(texto)

    if not linhas:
        return []
    return client.table("perguntas").insert(linhas).execute().data


def gerar_perguntas_intencao(usuaria_id: str, resumo: str) -> list[dict]:
    resposta = gerar(PROMPT_PERGUNTAS_INTENCAO.format(resumo=resumo), tarefa="entrevista_perguntas")
    perguntas_texto = parse_json_array(resposta)

    linhas = [
        {"usuaria_id": usuaria_id, "rodada": 1, "texto": p}
        for p in perguntas_texto
        if p and p.strip()
    ]
    client = get_client(admin=True)
    inserido = client.table("perguntas").insert(linhas).execute()
    return inserido.data


def registrar_resposta(pergunta_id: str, resposta_texto: str) -> dict:
    client = get_client(admin=True)
    pergunta = client.table("perguntas").select("*").eq("id", pergunta_id).execute().data[0]

    prompt_evidencia = PROMPT_EVIDENCIA_RESPOSTA.format(
        pergunta=pergunta["texto"], resposta=resposta_texto
    )
    resposta_ia = gerar(prompt_evidencia, tarefa="extracao_pdf")
    itens = parse_json_array(resposta_ia)

    # pergunta gerada pra resolver um gap (Entrevista 2) marca a evidência
    # com fonte "gap_resolvido" em vez de "entrevista" — é o rastro que
    # a Fase 7.4 do briefing exige entre gap e evidência que o fechou.
    fonte = "gap_resolvido" if pergunta.get("gap_id") else "entrevista"
    linhas_evidencia = [
        {
            "usuaria_id": pergunta["usuaria_id"],
            "texto": item["texto"],
            "tags": item.get("tags", []),
            "fonte": fonte,
        }
        for item in itens
        if item.get("texto")
    ]

    evidencia_id = None
    if linhas_evidencia:
        inseridas = client.table("evidencias").insert(linhas_evidencia).execute().data
        evidencia_id = inseridas[0]["id"]  # perguntas.gerou_evidencia_id guarda só a primeira

        # só fecha o gap se a resposta realmente rendeu evidência — se
        # não rendeu, o gap continua aberto em vez de fechar sem lastro.
        if pergunta.get("gap_id"):
            client.table("gaps").update(
                {"status": "resolvido", "evidencia_resolvida_id": evidencia_id}
            ).eq("id", pergunta["gap_id"]).execute()

    atualizado = (
        client.table("perguntas")
        .update(
            {
                "resposta": resposta_texto,
                "respondida_em": datetime.now(timezone.utc).isoformat(),
                "gerou_evidencia_id": evidencia_id,
            }
        )
        .eq("id", pergunta_id)
        .execute()
    )
    return atualizado.data[0]
