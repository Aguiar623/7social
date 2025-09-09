import requests
import json
from Utils.Analisis import analizar_emocion
    
def ejecutar_analisis(user_id):
    try:
        user_id = str(user_id)
        # Primero, obtener el nombre del usuario
        res_name = requests.get(f"http://localhost:8000/user/{user_id}/name")
        res_name.raise_for_status()  # Verifica que la solicitud se haya completado correctamente
        user_data = res_name.json()
        usuario_nombre = user_data["name"]  # Obtener el nombre del usuario
        
        # Obtener las publicaciones recientes del usuario
        res_posts = requests.get(f"http://localhost:8000/user/{user_id}/recent_posts")
        res_posts.raise_for_status()  # Verifica que la solicitud se haya completado correctamente
        posts = res_posts.json()

        if not posts:
            print("⚠️ No hay publicaciones recientes.")
            return False
        
        # Realizar el análisis de emociones basado en las publicaciones
        analisis = analizar_emocion(posts)

        if not analisis:
            print("No se pudo analizar las publicaciones")

        emocion = analisis.output
        probas = analisis.probas

        # Cargar los resultados previos (si existen) para no sobrescribirlos
        try:
            with open("estado_emocional.json", "r", encoding="utf-8") as f:
                resultados_existentes = json.load(f)
        except FileNotFoundError:
            # Si el archivo no existe, creamos un diccionario vacío
            resultados_existentes = {}

        # Agregar el nuevo análisis al diccionario
        resultados_existentes[user_id] = {
            "usuario": usuario_nombre,  # Ahora usamos el nombre del usuario
            "emocion": emocion,
            "probas": probas
        }

        # Guardar todos los resultados (incluyendo el nuevo) en el archivo
        with open("estado_emocional.json", "w", encoding="utf-8") as f:
            json.dump(resultados_existentes, f, ensure_ascii=False, indent=2)

        print(f"✅ Análisis automático completado para el usuario {usuario_nombre} ({user_id})")
        return True

    except Exception as e:
        print(f"❌ Error en el análisis: {e}")
        return False

