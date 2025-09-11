import streamlit as st
import json, re, os
import os
import requests
import random
from datetime import datetime
import pandas as pd
from urllib.parse import quote
from mastodon import Mastodon
from Utils.Analisis import analizar_emocion

st.title("7Chatbot")
st.write("Recomendaciones según tu **emoción actual**.")

# seleccion de fuente
modo = st.radio("Fuente de emoción:", ["Chatbot local", "Mastodon"])
emocion = None  # inicializamos
user_id = None  # inicializamos
usuario_nombre = None

if modo == "Mastodon":
    # Crear la app si no existe
    if not os.path.exists("mastodon_clientcred.secret"):
        Mastodon.create_app(
            "7ChatbotApp",
            api_base_url="https://mastodon.social",
            to_file="mastodon_clientcred.secret",
            redirect_uris="urn:ietf:wg:oauth:2.0:oob",
        )

    # Cargar credenciales de cliente
    mastodon = Mastodon(
        client_id="mastodon_clientcred.secret",
        api_base_url="https://mastodon.social"
    )

    # Si ya tenemos token en la sesión → usarlo directo
    if "mastodon_token" in st.session_state:
        mastodon = Mastodon(
            access_token=st.session_state.mastodon_token,
            api_base_url="https://mastodon.social",
        )
        usuario_nombre = mastodon.me()["acct"]
        st.success(f"✅ Sesión iniciada como {usuario_nombre}")

    else:
        # URL de login
        login_url = mastodon.auth_request_url(scopes=["read"])
        st.markdown(f"[🔑 Iniciar sesión con Mastodon]({login_url})")

        # Ver si Mastodon redirigió con ?code=...
        query_params = st.query_params
        if "code" in query_params:
            auth_code = (
                query_params["code"][0]
                if isinstance(query_params["code"], list)
                else query_params["code"]
            )
        else:
            auth_code = st.text_input("Pega aquí el código de autorización de Mastodon")

        if auth_code:  # cambiar code por access token
            access_token = mastodon.log_in(
                code=auth_code,
                scopes=["read"],
                redirect_uri="urn:ietf:wg:oauth:2.0:oob",
            )

            # Guardar token en la sesión (no en archivo)
            st.session_state.mastodon_token = access_token
            st.success("✅ Sesión iniciada con Mastodon")

            mastodon = Mastodon(
                access_token=st.session_state.mastodon_token,
                api_base_url="https://mastodon.social",
            )
            usuario_nombre = mastodon.me()["acct"]

    # Si ya hay usuario autenticado
    if "mastodon_token" in st.session_state:
        st.write(f"👤 Usuario: {usuario_nombre}")

        # Último toot
        posts = mastodon.account_statuses(mastodon.me()["id"], limit=1)
        if posts:
            texto = re.sub(r"<[^>]+>", "", posts[0]["content"])
            st.write(f"📝 Último toot: {texto}")

            # Analizar emoción
            analisis = analizar_emocion(texto)
            emocion = analisis.output
            st.markdown(f"**Emoción detectada:** `{emocion}`")

elif modo == "Chatbot local":
    query_params = st.query_params
    user_id = query_params.get("user_id", [None])[0]

    if user_id:
        res_name = requests.get(f"http://localhost:8000/user/{user_id}/name")
        res_name.raise_for_status()
        user_data = res_name.json()
        usuario_nombre = user_data["name"]

        if os.path.exists("estado_emocional.json"):
            with open("estado_emocional.json", "r", encoding="utf-8") as f:
                datos = json.load(f)
            user_data = datos.get(str(user_id), None)
            if user_data:
                emocion = user_data["emocion"]

        if emocion:
            st.markdown(f"**Emoción detectada (local):** `{emocion}`")
        else:
            st.error(f"No se encontró emoción para el usuario {usuario_nombre}.")
            st.stop()

        st.markdown(f"**Emoción detectada:** `{emocion}`")

if usuario_nombre and emocion:

    def cargar_titulos():
        try:
            with open("titulos.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error al cargar los géneros: {e}")
            return None

    def seleccionar_titulo(titulos, tipo):
        if tipo == "Libro":
            return random.choice(titulos.get("titulos_libros", []))
        elif tipo == "Película":
            return random.choice(titulos.get("titulos_peliculas", []))
        elif tipo == "Evento":
            return random.choice(titulos.get("titulos_eventos", []))

    titulos = cargar_titulos()

    def buscar_api_libro(titulo_aleatorio):
        for _ in range(5):
            titulo_encoded = quote(titulo_aleatorio)
            url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{titulo_encoded}"
            r = requests.get(url).json()
            if "items" in r:
                for item in r["items"]:
                    info = item.get("volumeInfo", {})
                    imagen = info.get("imageLinks", {}).get("thumbnail", "")
                    descripcion = info.get("description", "")
                    if imagen and descripcion:
                        return {
                            "titulo": info.get("title", "Título desconocido"),
                            "autor": ", ".join(info.get("authors", ["Autor desconocido"])),
                            "imagen": imagen,
                            "descripcion": descripcion,
                        }

    def buscar_api_pelicula(titulo_aleatorio):
        omdb_key = "b0f7d269"
        for _ in range(5):
            titulo_encoded = quote(titulo_aleatorio)
            url = f"http://www.omdbapi.com/?t={titulo_encoded}&apikey={omdb_key}"
            r = requests.get(url).json()
            poster = r.get("Poster", "")
            plot = r.get("Plot", "")
            titulo = r.get("Title", titulo_aleatorio)

            if poster and poster != "N/A" and plot and plot != "N/A":
                return {
                    "titulo": titulo,
                    "poster": poster,
                    "plot": plot,
                }

    def buscar_api_evento(titulo_aleatorio):
        apikey = "2l39pYhlAH1CmKry7R0aoqTUhFCdeFm7"
        for _ in range(2):
            titulo_encoded = quote(titulo_aleatorio)
            url = f"https://app.ticketmaster.com/discovery/v2/events.json?apikey={apikey}&keyword={titulo_encoded}&size=1"
            r = requests.get(url).json()
            eventos = r.get("_embedded", {}).get("events", [])
            if eventos:
                seleccion = random.choice(eventos)
                titulo = seleccion.get("name", "Evento sin nombre")
                descripcion = seleccion.get("info") or seleccion.get("pleaseNote", "")
                imagen = (
                    seleccion["images"][0]["url"]
                    if seleccion.get("images")
                    else None
                )
                lugar = (
                    seleccion.get("_embedded", {})
                    .get("venues", [{}])[0]
                    .get("name", "Lugar no disponible")
                )
                fecha_iso = (
                    seleccion.get("dates", {})
                    .get("start", {})
                    .get("dateTime", None)
                )
                fecha_formateada = "Fecha no disponible"
                if fecha_iso:
                    try:
                        fecha_str = fecha_iso.split(".")[0].replace("Z", "")
                        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M:%S")
                        fecha_formateada = fecha_obj.strftime("%d/%m/%Y a las %H:%M")
                    except Exception as e:
                        st.error(f"Error al convertir fecha: {e}")
                if titulo and imagen and descripcion:
                    return {
                        "titulo": titulo,
                        "descripcion": descripcion[:300],
                        "imagen": imagen,
                        "lugar": lugar,
                        "fecha": fecha_formateada,
                    }

    # === Cargar matriz de calificaciones ===
    def cargar_calificaciones(path="asociaciones.json", tipo=None, emocion=None):
        try:
            with open(path, "r", encoding="utf-8") as f:
                contenido = f.read()
                if not contenido.strip():
                    return pd.DataFrame()
                data = json.loads(contenido)
        except Exception as e:
            st.error(f"Error al leer {path}: {e}")
            return pd.DataFrame()

        rows = []
        for usuario, emociones in data.items():
            if emocion in emociones and tipo in emociones[emocion]:
                titulos = emociones[emocion][tipo]
                for titulo, detalles in titulos.items():
                    calificacion = detalles.get("calificacion")
                    if calificacion is not None:
                        rows.append(
                            {
                                "usuario": usuario,
                                "titulo": titulo,
                                "calificacion": detalles.get("calificacion", 0),
                            }
                        )
        df = pd.DataFrame(rows)
        return df

    # === Inicializar variables en session_state ===
    generar_nueva = st.button("🎲 Generar Nueva Recomendación")

    if "recomendaciones_ordenadas" not in st.session_state:
        st.session_state.recomendaciones_ordenadas = []
    if "recomendacion_index" not in st.session_state:
        st.session_state.recomendacion_index = 0
    if "tipo" not in st.session_state:
        st.session_state.tipo = None
    if "recomendacion" not in st.session_state:
        st.session_state.recomendacion = None

    tipo = st.selectbox(
        "¿Qué te gustaría que te recomiende hoy?", ("Libro", "Película", "Evento")
    )

    # === Generar nueva recomendación si cambia el tipo o se pide explícitamente ===
    if st.session_state.tipo != tipo or generar_nueva:
        if st.session_state.tipo != tipo:
            st.session_state.recomendacion_index = 0
            st.session_state.recomendaciones_ordenadas = []

        df = cargar_calificaciones(tipo=tipo, emocion=emocion)

        def obtener_recomendaciones_populares(df, usuario, top_n=5):
            if df.empty:
                return []
            titulos_usuario = df[df["usuario"] == usuario]["titulo"].tolist()
            df_altas = df[df["calificacion"] >= 4]
            populares = (
                df_altas[~df_altas["titulo"].isin(titulos_usuario)]
                .groupby("titulo")
                .size()
                .sort_values(ascending=False)
                .head(top_n)
                .index.tolist()
            )
            return populares

        if df.empty or "calificacion" not in df.columns:
            matriz = pd.DataFrame()
        else:
            matriz = df.pivot_table(
                index="usuario", columns="titulo", values="calificacion"
            )

            usar_colaborativo = False
            recomendaciones = {}

            if not matriz.empty and usuario_nombre in matriz.index:
                calificaciones_usuario = matriz.loc[usuario_nombre]
                items_preferidos = calificaciones_usuario[
                    calificaciones_usuario >= 4
                ]

                if len(items_preferidos) >= 2:
                    usar_colaborativo = True
                    diferencias = {}
                    frecuencias = {}

                    for user, ratings in matriz.iterrows():
                        rated_items = ratings.dropna()
                        for i in rated_items.index:
                            for j in rated_items.index:
                                if i != j:
                                    diferencias.setdefault((i, j), 0.0)
                                    frecuencias.setdefault((i, j), 0)
                                    diferencias[(i, j)] += (
                                        rated_items[i] - rated_items[j]
                                    )
                                    frecuencias[(i, j)] += 1

                    predicciones = {}
                    conteos = {}

                    for item_p, rating_p in items_preferidos.items():
                        for item in matriz.columns:
                            if item == item_p or item in items_preferidos:
                                continue
                            pair = (item, item_p)
                            if pair in diferencias and frecuencias[pair] > 0:
                                predicciones.setdefault(item, 0.0)
                                conteos.setdefault(item, 0)
                                predicciones[item] += (
                                    diferencias[pair] / frecuencias[pair]
                                ) + rating_p
                                conteos[item] += 1

                    recomendaciones = {
                        item: predicciones[item] / conteos[item]
                        for item in predicciones
                        if conteos[item] > 0
                        and pd.isna(calificaciones_usuario.get(item))
                    }

        if "usar_colaborativo" not in st.session_state:
            st.session_state.usar_colaborativo = False
        
        if st.session_state.usar_colaborativo and recomendaciones:
            st.info("Usando algoritmo Slope One para recomendación.")
            st.session_state.recomendaciones_ordenadas = sorted(
                recomendaciones.items(), key=lambda x: x[1], reverse=True
            )
        else:
            st.info("Usando recomendaciones basadas en emoción y popularidad.")
            titulos_populares = obtener_recomendaciones_populares(
                df, usuario_nombre, top_n=5
            )
            st.session_state.recomendaciones_ordenadas = [
                (titulo, 1.0) for titulo in titulos_populares
            ]

        # === Intentar recomendar según la lista ===
        recomendacion = None
        intentos_maximos = 5
        intentos = 0

        if st.session_state.recomendacion_index < len(
            st.session_state.recomendaciones_ordenadas
        ):
            titulo_aleatorio = st.session_state.recomendaciones_ordenadas[
                st.session_state.recomendacion_index
            ][0]
            st.session_state.recomendacion_index += 1
        else:
            while not recomendacion and intentos < intentos_maximos:
                titulo_aleatorio = seleccionar_titulo(titulos, tipo)
                if tipo == "Libro":
                    recomendacion = buscar_api_libro(titulo_aleatorio)
                elif tipo == "Película":
                    recomendacion = buscar_api_pelicula(titulo_aleatorio)
                elif tipo == "Evento":
                    recomendacion = buscar_api_evento(titulo_aleatorio)
                intentos += 1

        if not recomendacion:
            if tipo == "Libro":
                recomendacion = buscar_api_libro(titulo_aleatorio)
            elif tipo == "Película":
                recomendacion = buscar_api_pelicula(titulo_aleatorio)
            elif tipo == "Evento":
                recomendacion = buscar_api_evento(titulo_aleatorio)

        st.session_state.recomendacion = recomendacion
        st.session_state.tipo = tipo

    # === Mostrar recomendación y formulario siempre que exista ===
    recomendacion = st.session_state.recomendacion

    if recomendacion:
        if tipo == "Libro":
            st.markdown(f"📚 **Libro recomendado:** {recomendacion['titulo']}")
            st.markdown(f"**Autor:** {recomendacion['autor']}")
            st.image(recomendacion["imagen"], width=160)
            st.markdown(f"**Descripción:** {recomendacion['descripcion']}")
        elif tipo == "Película":
            st.markdown(f"🎬 **Película recomendada:** {recomendacion['titulo']}")
            poster = recomendacion.get("poster", "")
            if poster and poster != "N/A":
                st.image(recomendacion["poster"], width=160)
            else:
                st.warning("🎞️ Esta película no tiene poster disponible.")
            plot = recomendacion.get("plot", "")
            if plot and plot != "N/A":
                st.markdown(f"**Sinopsis:** {recomendacion['plot']}")
            else:
                st.warning("Esta película no tiene sinopsis disponible.")
        elif tipo == "Evento":
            st.markdown(f"📅 **Evento recomendado:** {recomendacion['titulo']}")
            st.image(recomendacion["imagen"], width=160)
            st.markdown(f"**Descripción:** {recomendacion['descripcion']}")
            st.markdown(f"📍 **Lugar:** {recomendacion['lugar']}")
            st.markdown(f"🕒 **Fecha y hora:** {recomendacion['fecha']}")

        # === Formulario de calificación ===
        with st.form("calificacion_form"):
            st.markdown("### ⭐ ¿Qué tan útil fue esta recomendación?")
            calificacion = st.slider("Califica de 1 (poco útil) a 5 (muy útil)", 1, 5, 3)
            submit_calificacion = st.form_submit_button("Enviar calificación")

        if submit_calificacion:
            titulo_recomendacion = recomendacion.get("titulo", "No disponible")
            asociaciones_path = "asociaciones.json"
            asociaciones = {}
            if os.path.exists(asociaciones_path):
                with open(asociaciones_path, "r", encoding="utf-8") as f:
                    asociaciones = json.load(f)

            if calificacion >= 4:
                asociaciones.setdefault(usuario_nombre, {}).setdefault(emocion, {}).setdefault(tipo, {})
                asociaciones[usuario_nombre][emocion][tipo][titulo_recomendacion] = {
                    "calificacion": calificacion
                }
                with open(asociaciones_path, "w", encoding="utf-8") as f:
                    json.dump(asociaciones, f, indent=4, ensure_ascii=False)
                st.success(f"¡Gracias por calificar con {calificacion} estrellas!")
                st.info("✅ ¡Tu calificación se ha guardado como una recomendación útil!")
    else:
        st.warning("⚠️ No se encontró una recomendación adecuada.")