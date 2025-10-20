7Social — Plataforma de Recomendación Emocional Basada en Texto

7Social es una plataforma social enfocada exclusivamente en texto, donde los usuarios pueden expresar cómo se sienten, interactuar con un chatbot emocional, y recibir recomendaciones personalizadas de libros, películas y eventos en función de su estado emocional y comportamiento dentro del sistema.

El ecosistema completo está dividido en dos componentes principales:

- Frontend (7Social App): interfaz social y de interacción del usuario.

- Backend (Chatbot Emocional y Sistema de Recomendación): lógica de análisis emocional, generación de contenido afectivo y filtrado colaborativo.

El sistema combina procesamiento del lenguaje natural, análisis afectivo y algoritmos de recomendación inteligentes para crear una experiencia emocionalmente adaptativa.

- Estructura del proyecto:

*FRONTEND*

Carpetas

SRC/ -> Raiz del proyecto

Subcarpetas

COMPONENTS/ -> SE ENCUENTRAN 3 COMPONENTES ESCENCIALES PARA EL SISTEMA EMOCIONAL Y DE RECOMENDACION

Componente Post.jsx -> Este componente representa las publicaciones (posts) dentro de la red social 7Social.
Cada publicación se compone de un título y un contenido textual. Es el núcleo de la interacción entre usuarios, ya que estas publicaciones sirven como insumo para el análisis emocional y la recopilación de datos que alimentan el sistema de recomendación.
En otras palabras, lo que los usuarios escriben aquí se analiza emocionalmente más adelante en el chatbot para ofrecer recomendaciones personalizadas.

Componente ChatbotWidget.jsx -> Este componente es el widget flotante del chatbot emocional dentro de la interfaz de 7Social.
Su propósito es conectar el frontend (React) con el chatbot en Streamlit que se ejecuta en Hugging Face Spaces.
El widget:

1.Verifica si el usuario ha iniciado sesión.

2.Consulta el backend (/user/{id}/posts_count) para asegurarse de que el usuario tenga al menos 3 publicaciones antes de permitirle usar el chatbot (esto fomenta la interacción dentro de la red).

3.Si cumple con la condición, abre un iframe con el chatbot emocional, pasando el user_id como parámetro en la URL (?user_id=).

4.Si no, muestra notificaciones usando react-toastify.

Componente ChatbotWidget.css -> es el diseño que se le aplica al chatbot

CONTEXT/ -> SE ENCUENTRA UN COMPONENTE DE AUTENTICACION DE LA RED SOCIAL

Componente Authcontext.jsx -> Este módulo implementa el contexto de autenticación global para la aplicación 7Social (frontend).
Permite que cualquier componente del proyecto conozca si el usuario está autenticado, pueda iniciar o cerrar sesión y sincronizar ese estado con el almacenamiento local del navegador (localStorage), Este contexto se usa en componentes como el Login, ChatbotWidget y Navbar, para controlar el acceso a funciones que requieren usuario autenticado.

PAGES/ -> SE ENCUENTRAN LOS COMPONENTES PRINCIPALES DE LA INTERFAZ

Componente Feed.jsx -> El componente Feed es el módulo central del frontend de 7Social, encargado de gestionar el muro de publicaciones donde los usuarios pueden compartir textos, reflexiones o emociones.
Este módulo también sirve como base de datos emocional, ya que los textos escritos alimentan el análisis afectivo del chatbot integrado en la misma interfaz.

Componente Feed.css -> es el diseño que se le aplica al feed principal.

Componente Home.jsx -> El componente Home constituye la pantalla principal del frontend de 7Social, gestionando tanto el inicio de sesión como el registro de nuevos usuarios.
Es el primer punto de contacto del usuario con la plataforma, combinando una interfaz visual atractiva con un flujo funcional claro que se conecta directamente al backend de autenticación.

Componente Home.css -> es el diseño que se le aplica a la pantalla principal.

Componente Navbar.jsx -> El componente Navbar representa la barra de navegación principal de la aplicación 7Social, visible únicamente cuando el usuario ha iniciado sesión correctamente.
Su propósito es proporcionar una navegación rápida entre las secciones principales del ecosistema (Inicio, Feed, Perfil) y ofrecer la funcionalidad de cerrar sesión de manera segura.

Componente Navbar.css -> es el diseño que se le aplica a la barra superior principal.

Componente Profile.jsx -> El componente Profile muestra la información personal del usuario autenticado dentro de la plataforma 7Social.
Su función principal es recuperar los datos almacenados localmente tras el inicio de sesión y renderizarlos en una vista limpia y centrada.

Componente Profile.css -> es el diseño que se le aplica a la sesion de informacion personal

SERVICE/ -> Se encuentra el enrutador hacia las peticiones del backend

Componente api.js -> Este módulo define la configuración del cliente HTTP principal para el frontend de 7Social, usando Axios para realizar todas las peticiones al backend.
Permite centralizar la gestión de solicitudes HTTP (login, registro, publicaciones, calificaciones, etc.) y garantiza que todas apunten al mismo servidor base. (esta se encuentra actualmente apuntando al servidor en linea, para probar en local deben apuntar hacia la misma localhost)

DENTRO DE LA SUBCARPETA SRC POR FUERA DE LAS SUBCARPETAS SE ENCUENTRAN LOS SIGUIENTE ELEMENTOS:

-App.jsx -> Este archivo constituye el punto de entrada principal del frontend de 7Social.
Define la estructura de navegación, la autenticación global, las rutas principales y los componentes persistentes (como la barra de navegación y las notificaciones).

-App.css -> es el diseño que se le aplica a la navegacion y componentes persistentes

Index.css -> Este archivo define los estilos globales del frontend de 7Social, combinando:

Estilos personalizados que controlan la tipografía, colores y disposición general de la interfaz.

Se carga automáticamente desde el punto de entrada principal (main.jsx) para aplicarse a toda la aplicación React.

Main.jsx -> Punto de entrada del frontend

POR FUERA DE LA CARPETA SRC SE ENCUENTRAN LOS SIGUIENTES ELEMENTOS:

default-avatar.jpg -> es una imagen la cual se utiliza en el perfil de la persona en la red social y se ubica en la parte del perfil ademas de el feed principal al lado izquierdo.

eslint.config.js,index.html -> archivos de configuracion del proyecto

package.json,package-lock.json -> librerias utilizadas para construir el proyecto

Versel.json -> archivo de configuracion para alinear la navegacion del enrutador que se encuentra en el servidor donde esta subido el front

PAGINA ONLINE DEL PROYECTO: https://7social-v3tt.vercel.app

Backend

Funcionamiento General

Usuario inicia sesión en la app móvil (7Social).

Escribe una publicación o conversa con el chatbot emocional.

El backend analiza el texto con pysentimiento y spaCy, detectando emociones y contexto.

Según la emoción, el sistema consulta las APIs externas:

OMDb → películas.

Google Books → libros.

Ticketmaster → eventos.

El sistema guarda las calificaciones en asociaciones.json.

A partir de 3 calificaciones altas (≥ 4 estrellas), se activa el filtrado colaborativo.

Las siguientes recomendaciones se ajustan al perfil emocional + patrones de comunidad.

Toda la experiencia se adapta al estado emocional detectado.
