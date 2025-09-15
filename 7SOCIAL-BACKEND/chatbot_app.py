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

    usuario_nombre = None

    # Intentar usar token previo
    if "mastodon_token" in st.session_state:
        try:
            mastodon = Mastodon(
                access_token=st.session_state.mastodon_token,
                api_base_url="https://mastodon.social",
            )
            usuario_nombre = mastodon.me()["acct"]  # valida token
            st.success(f"✅ Sesión iniciada como {usuario_nombre}")
        except Exception:
            st.warning("⚠️ Token inválido o expirado. Inicia sesión de nuevo.")
            del st.session_state["mastodon_token"]

    # Si no hay token válido → mostrar login
    if not usuario_nombre:
        login_url = mastodon.auth_request_url(scopes=["read"])
        st.markdown(f"[🔑 Iniciar sesión con Mastodon]({login_url})")

        auth_code = st.text_input("Pega aquí el código de autorización de Mastodon")

        if auth_code:
            try:
                access_token = mastodon.log_in(
                    code=auth_code,
                    scopes=["read"],
                    redirect_uri="urn:ietf:wg:oauth:2.0:oob",
                )
                st.session_state.mastodon_token = access_token
                st.rerun()
            except Exception as e:
                st.error(f"Error al autenticar: {e}")

    # Si tenemos token válido → mostrar info
    if usuario_nombre:
        st.write(f"👤 Usuario: {usuario_nombre}")

        try:
            posts = mastodon.account_statuses(mastodon.me()["id"], limit=1)
            if posts:
                texto = re.sub(r"<[^>]+>", "", posts[0]["content"])
                st.write(f"📝 Último toot: {texto}")

                analisis = analizar_emocion(texto)
                emocion = analisis.output
                if emocion:
                    st.markdown(f"**Emoción detectada:** `{emocion}`")
            else:
                st.warning("⚠️ No se encontró ningún toot para analizar.")
        except Exception as e:
            st.error(f"Error al obtener toots: {e}")

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
    # === Cargar títulos desde JSON ===
    def cargar_titulos():
        try:
            with open("titulos.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error al cargar los títulos: {e}")
            return None

    def seleccionar_titulo(titulos, tipo):
        if tipo == "Libro":
            return random.choice(titulos.get("titulos_libros", []))
        elif tipo == "Película":
            return random.choice(titulos.get("titulos_peliculas", []))
        elif tipo == "Evento":
            return random.choice(titulos.get("titulos_eventos", []))
    titulos = cargar_titulos()
    # === APIs para búsqueda de información ===
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
                imagen = seleccion["images"][0]["url"] if seleccion.get("images") else None
                lugar = seleccion.get("_embedded", {}).get("venues", [{}])[0].get("name", "Lugar no disponible")
                fecha_iso = seleccion.get("dates", {}).get("start", {}).get("dateTime", None)
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
            for emocion_key, tipos in emociones.items():
                for tipo_item, titulos in tipos.items():
                    for titulo, detalles in titulos.items():
                        calificacion = detalles.get("calificacion")
                        if calificacion is not None:
                            rows.append({
                                "usuario": usuario,
                                "emocion": emocion_key,
                                "tipo": tipo_item,
                                "titulo": titulo,
                                "calificacion": calificacion,
                            })

        df = pd.DataFrame(rows)
        if tipo:
            df = df[df["tipo"] == tipo]
        if emocion:
            df = df[df["emocion"] == emocion]
        return df
    # === Inicializar variables de estado ===
    generar_nueva = st.button("🎲 Generar Nueva Recomendación")

    if "recomendaciones_ordenadas" not in st.session_state:
        st.session_state.recomendaciones_ordenadas = []
    if "recomendacion_index" not in st.session_state:
        st.session_state.recomendacion_index = 0
    if "recomendacion_actual" not in st.session_state:
        st.session_state.recomendacion_actual = None
    if "tipo" not in st.session_state:
        st.session_state.tipo = None
    
    tipo = st.selectbox("¿Qué te gustaría que te recomiende hoy?", ("Libro", "Película", "Evento"))

    # === Generar nueva recomendación si cambia el tipo o se pide explícitamente ===
    if st.session_state.tipo != tipo:
        st.session_state.tipo = tipo
        st.session_state.recomendacion_actual = None
        st.session_state.recomendacion_index = 0
        st.session_state.recomendaciones_ordenadas = []
    
    if generar_nueva:
        st.session_state.recomendacion_actual = None
        
        if st.session_state.recomendaciones_ordenadas:
            if st.session_state.recomendacion_index >= len(st.session_state.recomendaciones_ordenadas):
                st.session_state.recomendacion_index = 0
                st.session_state.recomendaciones_ordenadas = []
        else:
        # Si no hay lista, reiniciamos índice
            st.session_state.recomendacion_index = 0

    # === Cargar calificaciones ===
    df = cargar_calificaciones(tipo=tipo, emocion=emocion)

    # === Obtener lista de títulos del tipo actual ===
    if df.empty:
        titulos_tipo_list = []
    else:
        titulos_tipo_list = df[df["tipo"] == tipo]["titulo"].dropna().unique().tolist()

    # === Función de popularidad con fallback ===
    def obtener_recomendaciones_populares(df_local, usuario, titulos_disponibles, top_n=5):
        if df_local.empty:
            if not titulos_disponibles:
                return []
            return random.sample(titulos_disponibles, min(top_n, len(titulos_disponibles)))

        titulos_usuario = df_local[df_local["usuario"] == usuario]["titulo"].tolist()
        df_altas = df_local[df_local["calificacion"] >= 4]

        populares = (
            df_altas[~df_altas["titulo"].isin(titulos_usuario)]
            .groupby("titulo")
            .size()
            .sort_values(ascending=False)
            .head(top_n)
            .index.tolist()
        )

        if not populares:
            disponibles = [t for t in titulos_disponibles if t not in titulos_usuario]
            if not disponibles:
                disponibles = titulos_disponibles
            if not disponibles:
                return []
            return random.sample(disponibles, min(top_n, len(disponibles)))

        return populares

    # === Crear matriz de utilidad ===
    if df.empty or "calificacion" not in df.columns:
        matriz = pd.DataFrame()
    else:
        matriz = df.pivot_table(index="usuario", columns="titulo", values="calificacion")

    usar_colaborativo = False
    recomendaciones = {}

    # === Algoritmo colaborativo (Slope One) ===
    if not matriz.empty and usuario_nombre in matriz.index:
        calificaciones_usuario = matriz.loc[usuario_nombre].dropna()
        items_preferidos = calificaciones_usuario[calificaciones_usuario >= 4]

        calificaciones_usuario = calificaciones_usuario[
        calificaciones_usuario.index.isin(titulos_tipo_list)
        ]
        items_preferidos = calificaciones_usuario[calificaciones_usuario >= 4]

        st.write(f"🔎 Ítems preferidos para {tipo}: {len(items_preferidos)}")
        st.write(f"📋 Lista: {items_preferidos.to_dict()}")

        if len(items_preferidos) >= 2:
            diferencias, frecuencias = {}, {}

            for user, ratings in matriz.iterrows():
                rated_items = ratings.dropna()
                rated_items = rated_items[rated_items.index.isin(titulos_tipo_list)]
                for i in rated_items.index:
                    for j in rated_items.index:
                        if i == j:
                            continue
                        diferencias.setdefault((i, j), 0.0)
                        frecuencias.setdefault((i, j), 0)
                        diferencias[(i, j)] += rated_items[i] - rated_items[j]
                        frecuencias[(i, j)] += 1
            
            st.write(f"📊 Pares de diferencias calculados: {len(diferencias)}")

            predicciones, conteos = {}, {}
            for item_p, rating_p in items_preferidos.items():
                for item in titulos_tipo_list:
                    if item == item_p or item in items_preferidos.index:
                        continue
                    pair = (item, item_p)
                    if pair in diferencias and frecuencias.get(pair, 0) > 0:
                        predicciones.setdefault(item, 0.0)
                        conteos.setdefault(item, 0)
                        predicciones[item] += (diferencias[pair] / frecuencias[pair]) + rating_p
                        conteos[item] += 1

            recomendaciones = {
                item: predicciones[item] / conteos[item]
                for item in predicciones
                if conteos.get(item, 0) > 0 and pd.isna(calificaciones_usuario.get(item))
            }

            st.write(f"📊 Recomendaciones generadas por Slope One: {len(recomendaciones)}")
            st.write(recomendaciones)
        
            if recomendaciones:
                usar_colaborativo = True
        else:
            st.write("⚠️ No hay suficientes items preferidos para activar colaborativo (se requieren ≥ 2).")

    st.session_state.usar_colaborativo = usar_colaborativo

    recomendaciones_ordenadas = []
    recomendacion = st.session_state.get("recomendacion_actual", None)
    fuente = None
# 1️ Populares
    titulos_populares = obtener_recomendaciones_populares(df, usuario_nombre, titulos_tipo_list, top_n=5)
    titulos_ya_calificados = df[df["usuario"] == usuario_nombre]["titulo"].tolist()
    titulos_populares = [t for t in titulos_populares if t not in titulos_ya_calificados]
    recomendaciones_ordenadas.extend([(t, 1.0) for t in titulos_populares])

# 2️ Slope One
    if usar_colaborativo and recomendaciones:
        slope_items = sorted(recomendaciones.items(), key=lambda x: x[1], reverse=True)
        recomendaciones_ordenadas.extend(slope_items)

    st.session_state.recomendaciones_ordenadas = recomendaciones_ordenadas

    titulo_aleatorio = None
# === Selección de la recomendación actual ===
    if st.session_state.recomendacion_actual is None:
        if st.session_state.recomendacion_index < len(st.session_state.recomendaciones_ordenadas):
            titulo_actual = st.session_state.recomendaciones_ordenadas[st.session_state.recomendacion_index][0]
            st.session_state.recomendacion_index += 1
            titulo_aleatorio = titulo_actual
        # Determinar fuente según posición
            fuente = "populares" if titulo_actual in titulos_populares else "slope"

        else:
        # Si se acaban todas, pasar a aleatorias
            fuente = "aleatorias"
            st.session_state.recomendacion_index = 0
            titulo_actual = seleccionar_titulo(titulos, tipo)

    # Para que se muestre siempre la fuente aunque no se haya recalculado
            
    st.write(f"🎯 **Fuente seleccionada:** {fuente}")
    st.write(f"📋 **Recomendaciones ordenadas:** {st.session_state.recomendaciones_ordenadas}")
    st.write(f"📊 **Índice actual:** {st.session_state.recomendacion_index}")
    st.write(f"📌 **usar_colaborativo:** {st.session_state.usar_colaborativo}")

    if recomendacion is None:
        for _ in range(5): 
            if fuente == "aleatorias":
                titulo_aleatorio = seleccionar_titulo(titulos, tipo)
            if tipo == "Libro":
                recomendacion = buscar_api_libro(titulo_aleatorio)
            elif tipo == "Película":
                recomendacion = buscar_api_pelicula(titulo_aleatorio)
            elif tipo == "Evento":
                recomendacion = buscar_api_evento(titulo_aleatorio)
            if recomendacion:
                break
            else:
                titulo_aleatorio = seleccionar_titulo(titulos, tipo)
        
        st.session_state.recomendacion_actual = recomendacion

    else:
    # Ya existe recomendación actual
        titulo_actual = recomendacion["titulo"]
        if st.session_state.recomendaciones_ordenadas:
            fuente = "populares" if not st.session_state.usar_colaborativo else "slope"
        else:
            fuente = "aleatorias"
    
    if fuente == "slope":
        st.info("📊 Usando algoritmo **Slope One** para recomendaciones.")
    elif fuente == "populares":
        st.info("🔥 Usando recomendaciones **basadas en popularidad**.")
    else:
        st.info("🎲 Usando recomendaciones **aleatorias**.")
    
    st.session_state.tipo = tipo

    # === Mostrar recomendación ===
    if recomendacion:
        # --- Mostrar según el tipo ---
        if tipo == "Libro":
            st.markdown(f"📚 **Libro recomendado:** {recomendacion['titulo']}")
            st.markdown(f"**Autor:** {recomendacion['autor']}")
            st.image(recomendacion["imagen"], width=160)
            st.markdown(f"**Descripción:** {recomendacion['descripcion']}")
        elif tipo == "Película":
            st.markdown(f"🎬 **Película recomendada:** {recomendacion['titulo']}")
            if recomendacion.get("poster", "") not in ("", "N/A"):
                st.image(recomendacion["poster"], width=160)
            plot = recomendacion.get("plot", "")
            if plot and plot != "N/A":
                st.markdown(f"**Sinopsis:** {plot}")
        elif tipo == "Evento":
            st.markdown(f"📅 **Evento recomendado:** {recomendacion['titulo']}")
            st.image(recomendacion["imagen"], width=160)
            st.markdown(f"**Descripción:** {recomendacion['descripcion']}")
            st.markdown(f"📍 **Lugar:** {recomendacion['lugar']}")
            st.markdown(f"🕒 **Fecha y hora:** {recomendacion['fecha']}")

        # --- Formulario de calificación ---
        with st.form("calificacion_form"):
            st.markdown("### ⭐ ¿Qué tan útil fue esta recomendación?")
            calificacion = st.slider("Califica de 1 (poco útil) a 5 (muy útil)", 1, 5, 3)
            submit_calificacion = st.form_submit_button("Enviar calificación")

        if submit_calificacion:
            asociaciones_path = "asociaciones.json"
            asociaciones = {}
            if os.path.exists(asociaciones_path):
                with open(asociaciones_path, "r", encoding="utf-8") as f:
                    asociaciones = json.load(f)

            if calificacion >= 4:
                asociaciones.setdefault(usuario_nombre, {}).setdefault(emocion, {}).setdefault(tipo, {})
                asociaciones[usuario_nombre][emocion][tipo][recomendacion["titulo"]] = {"calificacion": calificacion}
                with open(asociaciones_path, "w", encoding="utf-8") as f:
                    json.dump(asociaciones, f, indent=4, ensure_ascii=False)
                st.success(f"¡Gracias por calificar con {calificacion} estrellas!")
                st.info("✅ ¡Tu calificación se ha guardado como una recomendación útil!")
    
            st.session_state.recomendacion_actual = None
    else:
        st.warning("⚠️ No se encontró una recomendación adecuada.")
