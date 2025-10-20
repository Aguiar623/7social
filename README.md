7Social — Plataforma de Recomendación Emocional Basada en Texto

7Social es una plataforma social enfocada exclusivamente en texto, donde los usuarios pueden expresar cómo se sienten, interactuar con un chatbot emocional, y recibir recomendaciones personalizadas de libros, películas y eventos en función de su estado emocional y comportamiento dentro del sistema.

El ecosistema completo está dividido en dos componentes principales:

Frontend (7Social App): interfaz social y de interacción del usuario.

Backend (Chatbot Emocional y Sistema de Recomendación): lógica de análisis emocional, generación de contenido afectivo y filtrado colaborativo.

El sistema combina procesamiento del lenguaje natural, análisis afectivo y algoritmos de recomendación inteligentes para crear una experiencia emocionalmente adaptativa.

Estructura del proyecto:

FrontEnd

Carpetas

SRC/ -> Raiz del proyecto

Sub Carpetas

Components/ -> en esta carpeta se encuentran 2 componentes importantes para la red social y el sistema de recomendacion.

Post.jsx -> Este componente representa las publicaciones (posts) dentro de la red social 7Social.
Cada publicación se compone de un título y un contenido textual. Es el núcleo de la interacción entre usuarios, ya que estas publicaciones sirven como insumo para el análisis emocional y la recopilación de datos que alimentan el sistema de recomendación.
En otras palabras, lo que los usuarios escriben aquí se analiza emocionalmente más adelante en el chatbot para ofrecer recomendaciones personalizadas.

ChatbotWidget.jsx -> Este componente es el widget flotante del chatbot emocional dentro de la interfaz de 7Social.
Su propósito es conectar el frontend (React) con el chatbot en Streamlit que se ejecuta en Hugging Face Spaces.
El widget:

1.Verifica si el usuario ha iniciado sesión.

2.Consulta el backend (/user/{id}/posts_count) para asegurarse de que el usuario tenga al menos 3 publicaciones antes de permitirle usar el chatbot (esto fomenta la interacción dentro de la red).

3.Si cumple con la condición, abre un iframe con el chatbot emocional, pasando el user_id como parámetro en la URL (?user_id=).

4.Si no, muestra notificaciones usando react-toastify.




Funcionamiento General

Usuario inicia sesión en la app móvil (7Social).

Escribe una publicación o conversa con el chatbot emocional.

El backend analiza el texto con pysentimiento y spaCy, detectando emociones y contexto.

Según la emoción, el sistema consulta las APIs externas:

🎬 OMDb → películas.

📚 Google Books → libros.

🎟️ Ticketmaster → eventos.

El sistema guarda las calificaciones en asociaciones.json.

A partir de 3 calificaciones altas (≥ 4 estrellas), se activa el filtrado colaborativo.

Las siguientes recomendaciones se ajustan al perfil emocional + patrones de comunidad.

Toda la experiencia se adapta al estado emocional detectado.
