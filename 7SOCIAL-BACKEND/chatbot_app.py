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
        if isinstance(titulos,list):
            return random.choice(titulos) if titulos else None
        
        if tipo == "Libro":
            return random.choice(titulos.get("titulos_libros", []))
        elif tipo == "Película":
            return random.choice(titulos.get("titulos_peliculas", []))
        elif tipo == "Evento":
            return random.choice(titulos.get("titulos_eventos", []))
        return None
    titulos = cargar_titulos()
    # === APIs para búsqueda de información ===
    def buscar_api_libro(titulo_aleatorio):   
        if not titulo_aleatorio:
            return None
        for _ in range(5):
            try:
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
            except Exception as e:
                st.error(f"Error al buscar el libro: {e}")
        return None

    def buscar_api_pelicula(titulo_aleatorio):
        if not titulo_aleatorio:
            return None
        omdb_key = "b0f7d269"
        for _ in range(5):
            try:
                titulo_encoded = quote(str(titulo_aleatorio))
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
            except Exception as e:
                st.error(f"Error al buscar la pelicula {e}")
        return None
    
    def buscar_api_evento(titulo_aleatorio):
        if not titulo_aleatorio:
            return None
        apikey = "2l39pYhlAH1CmKry7R0aoqTUhFCdeFm7"
        for _ in range(2):
            try:
                titulo_encoded = quote(str(titulo_aleatorio))
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
            except Exception as e:
                st.error(f"Error al buscar evento: {e}")
        return None       
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
    if "recomendaciones_ordenadas" not in st.session_state:
        st.session_state.recomendaciones_ordenadas = []
    if "recomendacion_index" not in st.session_state:
        st.session_state.recomendacion_index = 0
    if "recomendacion_actual" not in st.session_state:
        st.session_state.recomendacion_actual = None
    if "tipo" not in st.session_state:
        st.session_state.tipo = None
    if "usar_colaborativo" not in st.session_state:
        st.session_state.usar_colaborativo = False
    if "historial_mostrados" not in st.session_state:
        st.session_state.historial_mostrados = set()
    if "titulos_populares" not in st.session_state or not isinstance(st.session_state.titulos_populares, dict):
        st.session_state.titulos_populares = {}
    if "fuente_actual" not in st.session_state:
        st.session_state.fuente_actual = "populares"
    if "recomendaciones_slope" not in st.session_state:
        st.session_state.recomendaciones_slope = []

    tipo = st.selectbox("¿Qué te gustaría que te recomiende hoy?", ("Libro", "Película", "Evento"))

    # === Generar nueva recomendación si cambia el tipo o se pide explícitamente ===
    if "tipo" not in st.session_state or st.session_state.tipo != tipo:
        st.session_state.tipo = tipo
        st.session_state.fuente_actual = "populares"
        st.session_state.recomendacion_actual = None
        st.session_state.recomendacion_index = 0
        st.session_state.recomendaciones_ordenadas = []
        if "titulo_aleatorio_guardado" in st.session_state:
            del st.session_state.titulo_aleatorio_guardado

    # === Cargar calificaciones y lista de titulos ===
    df = cargar_calificaciones(tipo=tipo, emocion=emocion)
    if df.empty:
        titulos_tipo_list = titulos.get(f"titulos_{tipo.lower()}s", []) if isinstance(titulos, dict) else []
    else:
        titulos_tipo_list = df[df["tipo"] == tipo]["titulo"].dropna().unique().tolist()
        if not titulos_tipo_list and isinstance(titulos, dict):
            titulos_tipo_list = titulos.get(f"titulos_{tipo.lower()}s", [])
    titulos_ya_calificados = df[df["usuario"] == usuario_nombre]["titulo"].tolist()

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
        calificaciones_usuario = calificaciones_usuario[calificaciones_usuario.index.isin(titulos_tipo_list)]
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
                recomendaciones_ordenadas = sorted(recomendaciones.items(), key=lambda x: x[1], reverse=True)
                ya_populares = set(st.session_state.titulos_populares.get(tipo, []))
                filtradas = [titulo for titulo, _ in recomendaciones_ordenadas if titulo not in ya_populares]

                st.session_state.recomendaciones_slope = filtradas
        else:    
            st.write("⚠️ No hay suficientes items preferidos para activar colaborativo (se requieren ≥ 2).")

    st.session_state.usar_colaborativo = usar_colaborativo
    st.session_state.titulos_populares.setdefault(tipo, [])
    
    ##-- recomendaciones ordenadas --##
    if not st.session_state.recomendaciones_ordenadas:
        excluidos_global = set(st.session_state.historial_mostrados) | set(titulos_ya_calificados)
    
        if usar_colaborativo and st.session_state.recomendaciones_slope:
            excluidos_global |= set(st.session_state.recomendaciones_slope)
    # 1) Populares preferidas (mantener comportamiento original)
        populares = obtener_recomendaciones_populares(df, usuario_nombre, titulos_tipo_list, top_n=5)
        populares = [t for t in populares if t not in excluidos_global]
        if populares:
            st.session_state.recomendaciones_ordenadas = populares
            st.session_state.fuente_actual = "populares"
            st.session_state.titulos_populares[tipo] = populares
            excluidos_global |= set(populares)
    # 2) Si no hay populares y hay slope disponible, usar slope
        if not st.session_state.recomendaciones_ordenadas and usar_colaborativo and st.session_state.recomendaciones_slope:
            excluidos_slope = excluidos_global | set(st.session_state.titulos_populares.get(tipo, []))
            slope_filtrado = [t for t in st.session_state.recomendaciones_slope if t not in excluidos_slope]
            if slope_filtrado:
                st.session_state.recomendaciones_ordenadas = slope_filtrado
                st.session_state.fuente_actual = "slope"
                excluidos_global |= set(slope_filtrado)
    # 3) Por último, aleatorias si no encontré nada arriba
        if not st.session_state.recomendaciones_ordenadas:
            excluidos = excluidos_global | set(st.session_state.titulos_populares.get(tipo, [])) | set(st.session_state.recomendaciones_slope)
            aleatorios = [t for t in titulos_tipo_list if t not in excluidos]
            if aleatorios:
                st.session_state.recomendaciones_ordenadas = random.sample(aleatorios, min(5, len(aleatorios)))
                st.session_state.fuente_actual = "aleatorias"

    # === Boton de recomendacion === #
    generar_nueva = st.button("🎲 Generar Nueva Recomendación")
    if generar_nueva:
        if st.session_state.recomendaciones_ordenadas:
            st.session_state.recomendacion_index += 1
            if st.session_state.recomendacion_index >= len(st.session_state.recomendaciones_ordenadas):
                if st.session_state.fuente_actual == "populares":
                    if st.session_state.usar_colaborativo and st.session_state.recomendaciones_slope:
                       st.session_state.recomendaciones_ordenadas = st.session_state.recomendaciones_slope.copy()
                       st.session_state.recomendacion_index = 0
                       st.session_state.fuente_actual = "slope"
                       st.write("lista populares terminada , pasando a slope one")
                    else:
                       st.session_state.recomendaciones_ordenadas = []
                       st.session_state.recomendacion_index = 0
                       st.session_state.fuente_actual = "aleatorias"
                       st.write("Lista de recomendaciones terminada, pasando a aleatorias")
                
                elif st.session_state.fuente_actual == "slope":
                    excluidos = set(st.session_state.historial_mostrados)
                    aleatorios = [t for t in titulos_tipo_list if t not in excluidos]
                    if aleatorios:
                        st.session_state.recomendaciones_ordenadas = random.sample(aleatorios, min(5, len(aleatorios)))
                        st.session_state.recomendacion_index = 0
                        st.session_state.fuente_actual = "aleatorias"
                        st.write("Lista de Slope One terminada, pasando a aleatorias")
                    else:
                        st.session_state.recomendaciones_ordenadas = []
                        st.session_state.recomendacion_index = 0
                        st.session_state.fuente_actual = "aleatorias"
                        st.write("No hay aleatorias disponibles, reiniciando flujo")

# === Selección de la recomendación actual ===
    titulo_actual = None
    fuente = st.session_state.fuente_actual
    recomendaciones_ordenadas = st.session_state.recomendaciones_ordenadas

    if st.session_state.recomendacion_actual is None:
        if st.session_state.recomendaciones_ordenadas:
            titulo_actual = st.session_state.recomendaciones_ordenadas[st.session_state.recomendacion_index]
            st.session_state.recomendacion_actual = {"titulo": titulo_actual, "fuente": st.session_state.fuente_actual}       
        else:
            titulos_excluir = set(st.session_state.historial_mostrados) | set(titulos_ya_calificados)
            aleatorios = [t for t in titulos_tipo_list if t not in titulos_excluir]
            if aleatorios:
                titulo_actual = random.choice(aleatorios)
                st.session_state.recomendacion_actual = {"titulo": titulo_actual, "fuente": "aleatorias"} 
    
    if titulo_actual and titulo_actual not in st.session_state.historial_mostrados:
        st.session_state.historial_mostrados.add(titulo_actual)

    #-------------DEBUG-------BORRAR AL REALIZAR
    st.write(f"🎯 **Fuente seleccionada:** {fuente}")
    st.write(f"📋 **Recomendaciones ordenadas:** {st.session_state.recomendaciones_ordenadas}")
    st.write(f"📊 **Índice actual:** {st.session_state.recomendacion_index}")
    st.write(f"📌 **usar_colaborativo:** {st.session_state.usar_colaborativo}")
        
    #-- recomendacion final --#
    recomendacion = None
    titulo_aleatorio = None
    if titulo_actual is None:
        if st.session_state.recomendacion_index < len(st.session_state.recomendaciones_ordenadas):
            titulo_actual = st.session_state.recomendaciones_ordenadas[st.session_state.recomendacion_index]
            st.session_state.recomendacion_actual = {"titulo": titulo_actual, "fuente": st.session_state.fuente_actual}
        else:    
            titulos_excluir = set(st.session_state.historial_mostrados) | set(titulos_ya_calificados)
            aleatorios = [t for t in titulos_tipo_list if t not in titulos_excluir]
            if aleatorios:
                titulo_actual = random.choice(aleatorios)
                st.session_state.recomendacion_actual = {"titulo": titulo_actual, "fuente": "aleatorias"} 
        
    if titulo_aleatorio:
        if tipo == "Libro":
            recomendacion = buscar_api_libro(titulo_aleatorio)
        elif tipo == "Película":
            recomendacion = buscar_api_pelicula(titulo_aleatorio)
        elif tipo == "Evento":
            recomendacion = buscar_api_evento(titulo_aleatorio)
        
        if recomendacion:
            recomendacion["fuente"] = fuente
            st.session_state.recomendacion_actual = recomendacion
            st.session_state.titulo_para_calificar = recomendacion["titulo"]
    else:
        if titulo_actual:
            if tipo == "Libro":
                recomendacion = buscar_api_libro(titulo_actual)
            elif tipo == "Película":
                recomendacion = buscar_api_pelicula(titulo_actual)
            elif tipo == "Evento":
                recomendacion = buscar_api_evento(titulo_actual)
            if recomendacion:
                recomendacion["fuente"] = fuente
                st.session_state.recomendacion_actual = recomendacion
                st.session_state.titulo_para_calificar = recomendacion["titulo"]
    
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
        # Usar el título guardado en session_state para evitar que se pierda en el rerun
            titulo_calificado = st.session_state.get("titulo_para_calificar", None)
            if titulo_calificado:
                asociaciones_path = "asociaciones.json"
                asociaciones = {}
                if os.path.exists(asociaciones_path):
                    with open(asociaciones_path, "r", encoding="utf-8") as f:
                        asociaciones = json.load(f)

                if calificacion >= 4:
                    asociaciones.setdefault(usuario_nombre, {}).setdefault(emocion, {}).setdefault(tipo, {})
                    asociaciones[usuario_nombre][emocion][tipo][titulo_calificado] = {"calificacion": calificacion}
                    with open(asociaciones_path, "w", encoding="utf-8") as f:
                        json.dump(asociaciones, f, indent=4, ensure_ascii=False)
                    st.success(f"¡Gracias por calificar con {calificacion} estrellas!")
                    st.info("✅ ¡Tu calificación se ha guardado como una recomendación útil!")
            else:
                if st.session_state.usar_colaborativo and st.session_state.get("recomendaciones_slope"):
                    st.session_state.recomendaciones_ordenadas = st.session_state.recomendaciones_slope
                    st.session_state.recomendacion_index = 0
                    st.session_state.fuente_actual = "slope"
                    st.write("🔄 Lista de populares terminada, pasando a Slope One ✅")
                else:
                    st.session_state.recomendaciones_ordenadas = []
                    st.session_state.recomendacion_index = 0
                    st.session_state.fuente_actual = "aleatorias"
                    st.write("🔄 Lista de recomendaciones terminada, pasando a aleatorias ✅")
    else:
        st.warning("⚠️ No se encontró una recomendación adecuada.")