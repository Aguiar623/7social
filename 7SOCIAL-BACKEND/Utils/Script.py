from mastodon import Mastodon
import json, re
from Utils.Analisis import analizar_emocion
import time

mastodon = Mastodon(
    access_token="ViyPaYQiwsBMxTdHcNcjOrWTfxjHdqHdiWKJgb0VG1Q",
    api_base_url="https://mastodon.social",
)


# Descargar publicaciones
def obtener_toots(max_publicaciones=25000):
    toots_totales = []
    max_id = None

    while len(toots_totales) < max_publicaciones:
        toots = mastodon.timeline_public(limit=40, max_id=max_id)

        if not toots:
            break

        toots_totales.extend(toots)
        max_id = toots[-1]["id"]
        print(f"Ahi {len(toots_totales)} publicaciones")
        time.sleep(1)

    hashtags = ["español", "noticias", "musica", "mexico", "colombia"]
    for tag in hashtags:
        toots_tag = mastodon.timeline_hashtag(tag, limit=25000)
        toots_totales.extend(toots_tag)

    unico = {t["id"]: t for t in toots_totales}
    return list(unico.values())


toots = obtener_toots(max_publicaciones=25000)

resultados = []
contador = 1

for toot in toots:
    # etiquetas HTML, limpiamos
    texto = re.sub(r"<[^>]+>", "", toot["content"])

    # Analizar emocion
    if texto:
        analisis = analizar_emocion(texto)
        if analisis:
            emocion = analisis.output
            emociones_prob = analisis.probas

            resultados.append(
                {
                    "id": contador,
                    "usuario": toot["account"]["acct"],
                    "texto": texto,
                    "emocion": emocion,
                    "probabilidades": emociones_prob,
                }
            )

            contador += 1

with open("emociones_API.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=4)

print(f"Analisis Completado. {contador-1} Publicaciones analizadas")
print(f"Resultado guardado en emociones_API.json")
