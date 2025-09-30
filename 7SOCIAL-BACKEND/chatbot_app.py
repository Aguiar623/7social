import streamlit as st
import json,os,requests
import os
import requests
import random
from datetime import datetime
import pandas as pd
from urllib.parse import quote
from openai import OpenAI

st.title("7Chatbot")
st.write("Recomendaciones según tu **emoción actual**.")

client = OpenAI(base_url="http://localhost:11434/v1", api_key="NO_KEY")  # Llama local

# --- Inicializar estado de chat ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "Eres un asistente que recomienda libros, películas o eventos según la emoción detectada."}]

# Mostrar historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

emocion = None  # inicializamos las variables
user_id = None
usuario_nombre = None

#obtenemos el usuario
query_params = st.query_params
user_id = query_params.get("user_id")

if isinstance(user_id, (list, tuple)):
    user_id = user_id[0] if user_id else None
if user_id is not None:
    user_id = str(user_id)

st.write(f"🆔 user_id detectado: {user_id}")

if user_id:
    try:
        res_name = requests.get(f"http://localhost:8000/user/{user_id}/name")
        res_name.raise_for_status()
        user_data = res_name.json()
        usuario_nombre = user_data["name"]
    except Exception as e:
        st.error(f"❌ No se pudo obtener el nombre del usuario: {e}")
        st.stop()

    if os.path.exists("estado_emocional.json"):
        with open("estado_emocional.json", "r", encoding="utf-8") as f:
            datos = json.load(f)
        user_data = datos.get(str(user_id), None)
        if user_data:
            emocion = user_data["emocion"]
        
    if emocion:
        st.markdown(f"**Emocion Detectada:** `{emocion}`")
        
    else:
        st.error(f"No se encontró emoción para el usuario {usuario_nombre}.")
        st.stop()

# --- Input de chat ---
if user_input := st.chat_input("Escribe aquí tu consulta..."):
    # Añadir mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Crear prompt con emoción incluida
    prompt = f"Usuario: {user_input}\nEmoción detectada: {emocion}\nResponde de forma breve y recomienda algo."

    # Enviar a Llama
    llama_response = client.chat.completions.create(
        model="llama3.1",
        messages=[
            *st.session_state.messages,
            {"role": "user", "content": prompt}
        ]
    )

    respuesta_llama = llama_response.choices[0].message.content

    # Mostrar respuesta
    with st.chat_message("assistant"):
        st.markdown(respuesta_llama)

    # Detectar tipo de recomendación
    tipo_detectado = "Película"
    if "libro" in user_input.lower():
        tipo_detectado = "Libro"
    elif "evento" in user_input.lower():
        tipo_detectado = "Evento"

    # Guardar mensaje del asistente y tipo
    st.session_state.messages.append({"role": "assistant", "content": respuesta_llama})
    st.session_state.messages.append({"role": "assistant", "content": f"📌 Entendido, buscaré un **{tipo_detectado}** para ti."})

    # === Cargar titulos desde JSON ===
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
    # === APIs para busqueda de información ===
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
    @st.cache_data(ttl=600, show_spinner=False)
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
                #st.write(f"🔎 Eventos encontrados para '{titulo_aleatorio}': {len(eventos)}")
                if eventos:
                    seleccion = random.choice(eventos)
                    titulo = seleccion.get("name", "Evento sin nombre")
                    descripcion = seleccion.get("info") or seleccion.get("pleaseNote", "Descripción no disponible")
                    imagen = seleccion["images"][0]["url"] if seleccion.get("images", "No tiene imagen Disponible") else None
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
                                "usuario": user,
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
        st.session_state.usar_colaborativo = False
    if "historial_mostrados" not in st.session_state:
        st.session_state.historial_mostrados = set()
    if "titulos_populares" not in st.session_state or not isinstance(st.session_state.titulos_populares, dict): 
        st.session_state.titulos_populares = {}
    if "usar_colaborativo" not in st.session_state: 
        st.session_state.usar_colaborativo = False
    if "fuente_actual" not in st.session_state:
        st.session_state.fuente_actual = "populares"
    if "recomendaciones_slope" not in st.session_state:
        st.session_state.recomendaciones_slope = []

    tipo = tipo_detectado

    mapa_tipos = {
    "libro": "libros",
    "película": "peliculas",
    "evento": "eventos"
    }
    clave_tipo = mapa_tipos.get(tipo.lower(), None)
    if not clave_tipo:
        st.error(f"Tipo '{tipo}' no reconocido")
        st.stop()
    
    # === Generar nueva recomendacion si cambia el tipo o se pide explicitamente ===
    if "tipo" not in st.session_state or st.session_state.tipo != tipo:
        st.session_state.tipo = tipo
        st.session_state.fuente_actual = "populares"
        st.session_state.recomendacion_actual = None
        st.session_state.recomendacion_index = 0
        st.session_state.recomendaciones_ordenadas = []
        if "titulo_aleatorio_guardado" in st.session_state:
            del st.session_state.titulo_aleatorio_guardado

    # === Cargar lista global de titulos desde JSON ===
    with open("titulos.json", "r", encoding="utf-8") as f:
        titulos = json.load(f)
    
    # === Cargar calificaciones y lista de titulos ===
    df = cargar_calificaciones(tipo=tipo, emocion=emocion)
    if df.empty:
        titulos_tipo_list = titulos.get(f"titulos_{clave_tipo}", []) if isinstance(titulos, dict) else []
    else:
        titulos_tipo_list = df[df["tipo"] == tipo]["titulo"].dropna().unique().tolist()
        if not titulos_tipo_list and isinstance(titulos, dict):
            titulos_tipo_list = titulos.get(f"titulos_{clave_tipo}", [])
    titulos_ya_calificados = df[df["usuario"] == user_id]["titulo"].tolist()

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

        #st.write(f"🔎 Ítems preferidos para {tipo}: {len(items_preferidos)}")
        #st.write(f"📋 Lista: {items_preferidos.to_dict()}")

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
            
            #st.write(f" Pares de diferencias calculados: {len(diferencias)}")

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

            #st.write(f" Recomendaciones generadas por Slope One: {len(recomendaciones)}")
            #st.write(recomendaciones)
            
            if recomendaciones:
                usar_colaborativo = True
                recomendaciones_ordenadas = sorted(recomendaciones.items(), key=lambda x: x[1], reverse=True)
                ya_populares = set(st.session_state.titulos_populares.get(tipo, []))
                filtradas = [titulo for titulo, _ in recomendaciones_ordenadas if titulo not in ya_populares]

                st.session_state.recomendaciones_slope = filtradas

    st.session_state.usar_colaborativo = usar_colaborativo
    st.session_state.titulos_populares.setdefault(tipo, [])
    
    ##-- recomendaciones ordenadas --##
    if not st.session_state.recomendaciones_ordenadas:
        excluidos_global = set(st.session_state.historial_mostrados) | set(titulos_ya_calificados)
        # Verificamos si el usuario tiene suficientes calificaciones para usar Slope One
        tiene_datos_para_slope = usar_colaborativo and st.session_state.recomendaciones_slope

        if tiene_datos_para_slope:
            slope_filtrado = [t for t in st.session_state.recomendaciones_slope if t not in excluidos_global]
            #st.write(" Slope crudo:", st.session_state.recomendaciones_slope)
            #st.write(" Filtrado:", slope_filtrado)
            
            if slope_filtrado:
                st.session_state.recomendaciones_ordenadas = slope_filtrado
                st.session_state.fuente_actual = "slope"
                excluidos_global |= set(slope_filtrado)

    # 1) Populares preferidas (mantener comportamiento original)
        if not st.session_state.recomendaciones_ordenadas:
            populares = obtener_recomendaciones_populares(df, usuario_nombre, titulos_tipo_list, top_n=5)
            populares = [t for t in populares if t not in excluidos_global]
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
            slope_filtrado = [t for t in populares if t not in excluidos_global]
            if slope_filtrado:
                st.session_state.recomendaciones_ordenadas = slope_filtrado
                st.session_state.fuente_actual = "slope"
                excluidos_global |= set(slope_filtrado)
    # 3) Por ultimo, aleatorias si no encontre nada arriba
        if not st.session_state.recomendaciones_ordenadas:
            excluidos_global |= set(st.session_state.titulos_populares.get(tipo, []))
            excluidos_global |= set(st.session_state.recomendaciones_slope)
            excluidos_global |= set(st.session_state.historial_mostrados)
            
            lista_global = titulos.get(f"titulos_{clave_tipo}", [])
            aleatorios = [t for t in lista_global if t not in excluidos_global]
            aleatorios = [t for t in aleatorios if t not in excluidos_global]

            if aleatorios:
                st.session_state.recomendaciones_ordenadas = random.sample(aleatorios, min(5, len(aleatorios)))
                st.session_state.recomendacion_index = 0
                st.session_state.fuente_actual = "aleatorias"
            else:
        # Si no hay mas en la lista local , llamar a API para traer algo nuevo
                lista_global = titulos.get(f"titulos_{clave_tipo}", [])
                aleatorios = [t for t in lista_global if t not in excluidos_global]
                if aleatorios:
                    titulo_actual = random.choice(aleatorios)
                    st.session_state.recomendacion_actual = {"titulo": titulo_actual, "fuente": "aleatorias"}

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
                       #st.write("lista populares terminada , pasando a slope one")
                    else:
                       st.session_state.recomendaciones_ordenadas = []
                       st.session_state.recomendacion_index = 0
                       st.session_state.fuente_actual = "aleatorias"
                       #st.write("Lista de recomendaciones terminada, pasando a aleatorias")
                
                elif st.session_state.fuente_actual == "slope":
                    excluidos_global = set(st.session_state.historial_mostrados)| set(titulos_ya_calificados)
                    excluidos_global |= set(st.session_state.titulos_populares.get(tipo, []))
                    excluidos_global |= set(st.session_state.recomendaciones_slope)
                    lista_global = titulos.get(f"titulos_{clave_tipo}", [])
                    aleatorios = [t for t in lista_global if t not in excluidos_global]
                    if aleatorios:
                        st.session_state.recomendaciones_ordenadas = random.sample(aleatorios, min(5, len(aleatorios)))
                        st.session_state.recomendacion_index = 0
                        st.session_state.fuente_actual = "aleatorias"
                        #st.write("Lista de Slope One terminada, pasando a aleatorias")
                    else:
                        st.session_state.recomendaciones_ordenadas = []
                        st.session_state.recomendacion_index = 0
                        st.session_state.fuente_actual = "aleatorias"
                        #st.write("No hay aleatorias disponibles, reiniciando flujo")

# === Seleccion de la recomendacion actual ===
    titulo_actual = None
    fuente = st.session_state.fuente_actual
    recomendaciones_ordenadas = st.session_state.recomendaciones_ordenadas

    # Crear conjunto de exclusion
    titulos_excluir = set(st.session_state.historial_mostrados) | set(titulos_ya_calificados)

    if st.session_state.recomendacion_actual is None:
        if st.session_state.recomendaciones_ordenadas:
            titulo_actual = st.session_state.recomendaciones_ordenadas[st.session_state.recomendacion_index]
            st.session_state.recomendacion_actual = {"titulo": titulo_actual, "fuente": st.session_state.fuente_actual}       
        else:
            lista_global = titulos.get(f"titulos_{clave_tipo}", [])
            aleatorios = [t for t in lista_global if t not in titulos_excluir]
            if aleatorios:
                titulo_actual = random.choice(aleatorios)
                st.session_state.recomendacion_actual = {"titulo": titulo_actual, "fuente": "aleatorias"} 
    
    if titulo_actual and titulo_actual not in st.session_state.historial_mostrados:
        st.session_state.historial_mostrados.add(titulo_actual)

    if "recomendaciones_slope" in st.session_state:
        rec_slope = st.session_state.recomendaciones_slope
        if isinstance(rec_slope, dict):
            titulos_excluir |= set(rec_slope.keys())
        elif isinstance(rec_slope, list):
        # Si es lista, agregamos los titulos directamente
            titulos_excluir |= set(rec_slope)

    #-------------DEBUG-------COMENTADO POR SI ALGUN BUG EN EL FUTURO-----
    #st.write(f" **Fuente seleccionada:** {fuente}")
    #st.write(f" **Recomendaciones ordenadas:** {st.session_state.recomendaciones_ordenadas}")
    #st.write(f" **Índice actual:** {st.session_state.recomendacion_index}")
    #st.write(f" **usar_colaborativo:** {st.session_state.usar_colaborativo}")
        
    #-- recomendacion final --#
    recomendacion = None
    titulo_aleatorio = None

    # Asegurar que hay una lista; si esta vacia, forzamos aleatorias simples (sin API en el filtro)
    if not st.session_state.recomendaciones_ordenadas:
        lista_global = titulos.get(f"titulos_{clave_tipo}", [])
        excluidos_global = set(st.session_state.historial_mostrados) | set(titulos_ya_calificados)
        aleatorios_raw = [t for t in lista_global if t not in excluidos_global]
        if aleatorios_raw:
            st.session_state.recomendaciones_ordenadas = random.sample(aleatorios_raw, min(5, len(aleatorios_raw)))
            st.session_state.recomendacion_index = 0
            st.session_state.fuente_actual = "aleatorias"

# Intentar hasta N candidatos de la lista ordenada evita llamadas infinitas
    max_intentos = 3
    intentos = 0
    found = False

    while intentos < max_intentos and st.session_state.recomendacion_index < len(st.session_state.recomendaciones_ordenadas):
        candidato = st.session_state.recomendaciones_ordenadas[st.session_state.recomendacion_index]
        #st.write(f"🎯 Intentando API para: {candidato}")
        try:
            if tipo == "Libro":
                rec = buscar_api_libro(candidato)
            elif tipo == "Película":
                rec = buscar_api_pelicula(candidato)
            elif tipo == "Evento":
                rec = buscar_api_evento(candidato)
            else:
                rec = None
        except Exception as e:
            rec = None
            #st.write("⚠️ Error llamando API para candidato:", candidato, e)

        if rec:
            rec["fuente"] = fuente
            st.session_state.recomendacion_actual = rec
            st.session_state.titulo_para_calificar = rec.get("titulo", candidato)
            recomendacion = rec
            found = True
            break
        else:
            #st.write(f"⚠️ No hay detalles para '{candidato}', probando siguiente...")
            st.session_state.historial_mostrados.add(candidato)
            st.session_state.recomendacion_index += 1
            intentos += 1

    if not found:
    # Si no obtuvimos nada en MAX intentos, regeneramos aleatorias limpias y rerun
        st.write("⚠️ No se encontraron recomendaciones válidas en la lista actual. Generando aleatorias...")
        lista_global = titulos.get(f"titulos_{clave_tipo}", [])
        excluidos_global = set(st.session_state.historial_mostrados) | set(titulos_ya_calificados)
        aleatorios_raw = [t for t in lista_global if t not in excluidos_global]
        if aleatorios_raw:
            st.session_state.recomendaciones_ordenadas = random.sample(aleatorios_raw, min(5, len(aleatorios_raw)))
            st.session_state.recomendacion_index = 0
            st.session_state.fuente_actual = "aleatorias"
        else:
            st.session_state.recomendaciones_ordenadas = []
            st.session_state.recomendacion_index = 0
        st.rerun()

    if fuente == "slope":
        st.info("📊 Usando algoritmo **Slope One** para recomendaciones.")
    elif fuente == "populares":
        st.info("🔥 Usando recomendaciones **basadas en popularidad**.")
    else:
        st.info("🎲 Usando recomendaciones **aleatorias**.")
    
    st.session_state.tipo = tipo

    # === Mostrar recomendacion ===
    if recomendacion:
        # --- Mostrar segun el tipo ---
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

        # --- Formulario de calificacion ---
        with st.form("calificacion_form"):
            st.markdown("### ⭐ ¿Qué tan útil fue esta recomendación?")
            calificacion = st.slider("Califica de 1 (poco útil) a 5 (muy útil)", 1, 5, 3)
            submit_calificacion = st.form_submit_button("Enviar calificación")
        
        if submit_calificacion:
            titulo_calificado = st.session_state.get("titulo_para_calificar", None)
            if titulo_calificado:
                asociaciones_path = "asociaciones.json"
                asociaciones = {}
                if os.path.exists(asociaciones_path):
                    with open(asociaciones_path, "r", encoding="utf-8") as f:
                        asociaciones = json.load(f)

                if calificacion >= 4:
                    asociaciones.setdefault(str(user_id), {}).setdefault(emocion, {}).setdefault(tipo, {})
                    asociaciones[str(user_id)][emocion][tipo][titulo_calificado] = {"calificacion": calificacion}
                    with open(asociaciones_path, "w", encoding="utf-8") as f:
                        json.dump(asociaciones, f, indent=4, ensure_ascii=False)
                    st.success(f"¡Gracias por calificar con {calificacion} estrellas!")
                    st.info("✅ ¡Tu calificación se ha guardado como una recomendación útil!")
                
                    st.session_state.historial_mostrados.add(titulo_calificado)
                
                    st.session_state.titulo_para_calificar = None
                    st.session_state.recomendacion_actual = None
        
                     # Avanzar indice si hay lista, o forzar regenerar aleatorias
                    if st.session_state.recomendaciones_ordenadas and st.session_state.recomendacion_index < len(st.session_state.recomendaciones_ordenadas) - 1:
                        st.session_state.recomendacion_index += 1
                    else:
            # forzamos nuevas aleatorias en el rerun
                        st.session_state.recomendaciones_ordenadas = []
                        st.session_state.recomendacion_index = 0
                        st.session_state.fuente_actual = "aleatorias" 
                    st.rerun()