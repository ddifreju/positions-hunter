"""Matching de vagas em duas camadas (Fase 3, Seção 7.2/7.4 do briefing).

Camada 1 (TF-IDF local, sem IA) corta o volume bruto de vagas coletadas
para um punhado de finalistas — barato, sem limite de requisição.
Camada 2 (IA) analisa só essas finalistas, gera score + justificativa,
e aponta habilidades que a vaga pede e o banco de evidências não cobre
(que viram gaps). Rodar IA em todas as vagas coletadas seria caro e
desnecessário (Seção 6.2) — a demanda mesmo é só nas finalistas.
"""

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from matchvagas.db import get_client
from matchvagas.evidencias import resumo_evidencias
from matchvagas.gaps import processar_habilidades_faltantes
from matchvagas.ia import gerar
from matchvagas.parsing import parse_json

# O corpus de vagas é multilíngue (PT/ES/EN). Sem isso, palavras
# comuns de português/espanhol dominam a similaridade e uma vaga de
# vendas em português fica "parecida" com o perfil só por compartilhar
# "experiência", "trabalho", "equipe" — nada a ver com a skill em si.
_STOPWORDS_PT_ES = {
    "de", "da", "do", "das", "dos", "em", "para", "com", "que", "não", "uma", "um",
    "uns", "umas", "os", "as", "ao", "aos", "à", "às", "é", "são", "foi", "ser",
    "ter", "tem", "seu", "sua", "seus", "suas", "mais", "muito", "também", "como",
    "quando", "onde", "qual", "quais", "este", "esta", "isso", "isto", "essa",
    "esse", "pelo", "pela", "por", "sem", "sobre", "entre", "até", "após", "antes",
    "depois", "então", "mas", "ou", "se", "na", "no", "nas", "nos", "e", "a", "o",
    "la", "el", "los", "las", "en", "con", "sin", "hasta", "después", "pero", "si",
    "un", "una", "unos", "unas", "son", "fue", "tener", "tiene", "su", "sus",
    "más", "muy", "también", "cuando", "donde", "cual", "cuales", "eso",
}
STOP_WORDS_MULTILINGUE = list(ENGLISH_STOP_WORDS | _STOPWORDS_PT_ES)

PROMPT_AVALIACAO_VAGA = """\
Você avalia a compatibilidade entre o perfil de uma candidata e uma vaga.

Perfil da candidata (evidências reais e preferências dela):
---
{perfil}
---

Vaga:
Título: {titulo}
Empresa: {empresa}
Descrição: {descricao}
---

Devolva APENAS um objeto JSON, sem texto antes ou depois, neste formato:
{{
  "score": <inteiro de 0 a 100, compatibilidade geral>,
  "justificativa": "frase curta e concreta citando o que casa e o que falta",
  "habilidades_faltantes": ["habilidade que a vaga pede e não aparece no perfil", ...]
}}

Só liste em habilidades_faltantes o que a vaga claramente pede. Não \
invente pedido que a vaga não faz nem habilidade que o perfil já cobre.
"""


def _texto_vaga(vaga: dict) -> str:
    return f"{vaga.get('titulo') or ''} {vaga.get('descricao') or ''}"


def _texto_perfil_tfidf(usuaria_id: str) -> str:
    """Texto do perfil pro TF-IDF: repete as tags de habilidade pra dar
    peso extra a elas. Nome de tecnologia/ferramenta tende a aparecer
    igual em vaga de qualquer idioma — é um sinal muito mais confiável
    que o texto corrido em português das evidências."""
    client = get_client(admin=True)
    linhas = client.table("evidencias").select("texto,tags").eq("usuaria_id", usuaria_id).execute().data
    textos = " ".join(linha["texto"] for linha in linhas)
    tags = [tag for linha in linhas for tag in linha["tags"]]
    return f"{textos} {' '.join(tags * 4)}"


def camada1_tfidf(usuaria_id: str, top_n: int = 15) -> list[dict]:
    client = get_client(admin=True)
    vagas = client.table("vagas").select("*").execute().data
    if not vagas:
        return []

    perfil = _texto_perfil_tfidf(usuaria_id)
    corpus = [_texto_vaga(v) for v in vagas]

    vetor = TfidfVectorizer(max_features=5000, stop_words=STOP_WORDS_MULTILINGUE)
    matriz = vetor.fit_transform(corpus + [perfil])
    similaridades = cosine_similarity(matriz[-1], matriz[:-1])[0]

    ordenado = sorted(zip(vagas, similaridades), key=lambda par: par[1], reverse=True)
    return [{"vaga": v, "score_tfidf": float(s)} for v, s in ordenado[:top_n]]


def camada2_ia(usuaria_id: str, finalistas: list[dict]) -> list[dict]:
    perfil = resumo_evidencias(usuaria_id)
    client = get_client(admin=True)
    resultados = []

    for item in finalistas:
        vaga = item["vaga"]
        prompt = PROMPT_AVALIACAO_VAGA.format(
            perfil=perfil,
            titulo=vaga.get("titulo") or "",
            empresa=vaga.get("empresa") or "",
            descricao=(vaga.get("descricao") or "")[:4000],
        )
        avaliacao = parse_json(gerar(prompt, tarefa="avaliacao_vaga"))

        candidatura = (
            client.table("candidaturas")
            .upsert(
                {
                    "usuaria_id": usuaria_id,
                    "vaga_id": vaga["id"],
                    "status": "descoberta",
                    "score": avaliacao["score"],
                    "justificativa_score": avaliacao["justificativa"],
                },
                on_conflict="usuaria_id,vaga_id",
            )
            .execute()
            .data[0]
        )

        habilidades_faltantes = avaliacao.get("habilidades_faltantes", [])
        gaps = processar_habilidades_faltantes(usuaria_id, habilidades_faltantes)

        resultados.append(
            {
                "vaga": vaga,
                "candidatura": candidatura,
                "gaps": gaps,
            }
        )

    return resultados


def rodar_matching(usuaria_id: str, top_n_tfidf: int = 15) -> list[dict]:
    finalistas = camada1_tfidf(usuaria_id, top_n=top_n_tfidf)
    return camada2_ia(usuaria_id, finalistas)
