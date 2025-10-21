7Social — Plataforma de Recomendación Emocional Basada en Texto

7Social es una plataforma social enfocada exclusivamente en texto, donde los usuarios pueden expresar cómo se sienten, interactuar con un chatbot emocional, y recibir recomendaciones personalizadas de libros, películas y eventos en función de su estado emocional y comportamiento dentro del sistema.

El ecosistema completo está dividido en dos componentes principales:

- Frontend (7Social App): interfaz social y de interacción del usuario.

- Backend (Chatbot Emocional y Sistema de Recomendación): lógica de análisis emocional, generación de contenido afectivo y filtrado colaborativo.

El sistema combina procesamiento del lenguaje natural, análisis afectivo y algoritmos de recomendación inteligentes para crear una experiencia emocionalmente adaptativa.

- Estructura del proyecto:

**FRONTEND**

Carpetas

- SRC/ -> Raiz del proyecto

Subcarpetas

- COMPONENTS/ -> SE ENCUENTRAN 3 COMPONENTES ESCENCIALES PARA EL SISTEMA EMOCIONAL Y DE RECOMENDACION

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

- CONTEXT/ -> SE ENCUENTRA UN COMPONENTE DE AUTENTICACION DE LA RED SOCIAL

Componente Authcontext.jsx -> Este módulo implementa el contexto de autenticación global para la aplicación 7Social (frontend).
Permite que cualquier componente del proyecto conozca si el usuario está autenticado, pueda iniciar o cerrar sesión y sincronizar ese estado con el almacenamiento local del navegador (localStorage), Este contexto se usa en componentes como el Login, ChatbotWidget y Navbar, para controlar el acceso a funciones que requieren usuario autenticado.

- PAGES/ -> SE ENCUENTRAN LOS COMPONENTES PRINCIPALES DE LA INTERFAZ

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

- SERVICE/ -> Se encuentra el enrutador hacia las peticiones del backend

Componente api.js -> Este módulo define la configuración del cliente HTTP principal para el frontend de 7Social, usando Axios para realizar todas las peticiones al backend.
Permite centralizar la gestión de solicitudes HTTP (login, registro, publicaciones, calificaciones, etc.) y garantiza que todas apunten al mismo servidor base. (esta se encuentra actualmente apuntando al servidor en linea, para probar en local deben apuntar hacia la misma localhost)

DENTRO DE LA SUBCARPETA SRC POR FUERA DE LAS SUBCARPETAS SE ENCUENTRAN LOS SIGUIENTE ELEMENTOS:

- App.jsx -> Este archivo constituye el punto de entrada principal del frontend de 7Social.
Define la estructura de navegación, la autenticación global, las rutas principales y los componentes persistentes (como la barra de navegación y las notificaciones).

- App.css -> es el diseño que se le aplica a la navegacion y componentes persistentes

- Index.css -> Este archivo define los estilos globales del frontend de 7Social, combinando:

Estilos personalizados que controlan la tipografía, colores y disposición general de la interfaz.

Se carga automáticamente desde el punto de entrada principal (main.jsx) para aplicarse a toda la aplicación React.

- Main.jsx -> Punto de entrada del frontend

POR FUERA DE LA CARPETA SRC SE ENCUENTRAN LOS SIGUIENTES ELEMENTOS:

- default-avatar.jpg -> es una imagen la cual se utiliza en el perfil de la persona en la red social y se ubica en la parte del perfil ademas de el feed principal al lado izquierdo.

- eslint.config.js,index.html -> archivos de configuracion del proyecto

- package.json,package-lock.json -> librerias utilizadas para construir el proyecto

- Versel.json -> archivo de configuracion para alinear la navegacion del enrutador que se encuentra en el servidor donde esta subido el front

- PAGINA ONLINE DEL PROYECTO: https://7social-v3tt.vercel.app
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
**BACKEND**

Carpetas

- .Streamlit

Archivo config.toml -> Este archivo define la configuración visual del entorno de Streamlit para el backend de 7Social, personalizando completamente la apariencia de la interfaz según los colores y estilos de la marca del proyecto. (solo aplica para entornos locales)

- Utils

Archivo Analisis_publicaciones.py -> Este módulo ejecuta el análisis emocional automático de las publicaciones más recientes de un usuario en 7Social.
Combina la comunicación con el backend (para obtener datos del usuario y sus posts) con el componente de análisis afectivo basado en pysentimiento y spaCy.

Archivo Analisis.py -> Este módulo implementa el análisis emocional de texto en español para la plataforma 7Social.
Utiliza pysentimiento (modelo robertuito) y spaCy (es_core_news_lg) para procesar, normalizar y evaluar el contenido textual que los usuarios publican en la red social.

El objetivo principal es detectar la emoción predominante en las publicaciones o conversaciones del usuario, generando una salida estructurada que el backend usa para personalizar recomendaciones afectivas.

Archivo Script.py -> Este módulo se encarga de recopilar publicaciones (toots) desde la red social Mastodon, procesarlas y aplicar el análisis emocional automático utilizando el modelo de pysentimiento.
Su propósito es generar un dataset emocional real en español para alimentar el modelo de recomendación y pruebas del sistema afectivo de 7Social.

Archivo Security.py -> Este módulo implementa las funciones de encriptación y verificación de contraseñas para el sistema, garantizando que la autenticación de los usuarios sea segura y moderna, Utiliza la librería Passlib con el algoritmo Argon2, considerado uno de los más seguros actualmente con lo cual Permite generar hashes únicos a partir de contraseñas en texto plano, evitando el almacenamiento de datos sensibles sin protección.

Archivo Test.py -> Archivo de pruebas unitarias encargado de verificar el correcto funcionamiento del módulo de análisis emocional. Utiliza la librería unittest para evaluar la precisión del modelo ante diferentes tipos de entradas textuales. Incluye casos con emociones positivas, negativas, vacías, múltiples textos, símbolos y entradas sin sentido, comprobando que el sistema siempre retorne una emoción válida y probabilidades que sumen a 1.

EN EL ARCHIVO RAIZ ENCONTRAMOS:

- Asociaciones.json -> Archivo de almacenamiento estructurado en formato JSON que guarda las asociaciones entre usuarios, emociones detectadas y los ítems calificados (libros, películas o eventos). Cada usuario se identifica por su ID y dentro de cada emoción se registran los elementos recomendados junto con su calificación, lo que permite al sistema mejorar el filtrado colaborativo y generar recomendaciones más precisas según el estado emocional.

- Database.py -> Este archivo configura la conexión principal con la base de datos PostgreSQL utilizada por el backend de 7Social. Define el motor, la sesion y la base declarativa para manejar modelos ORM con SQLAlchemy

- Emociones_API.json -> Este archivo almacena los resultados del análisis emocional automático realizado sobre publicaciones obtenidas desde la red social Mastodon.
Cada entrada representa un toot procesado junto con la emoción dominante detectada y las probabilidades asociadas a cada categoria emocional.

- estado_emocional.json -> Este archivo almacena el estado emocional actual de cada usuario registrado en la plataforma 7Social, calculado a partir de sus publicaciones recientes y procesado por el módulo de análisis afectivo.

- Main.py -> Este archivo constituye el nucleo del backend de la aplicacion 7Social, combinando los servicios de FastAPI y Streamlit en un entorno unificado.
Se encarga de gestionar la autenticación, las publicaciones, la conexión con la base de datos PostgreSQL, y la ejecución automática del análisis emocional basado en texto.

- Models.py -> Este archivo define el modelo de datos principal del sistema 7Social, implementado con SQLAlchemy ORM para mapear las entidades del sistema hacia la base de datos PostgreSQL.
Aquí se declaran las tablas users y posts, así como sus relaciones y atributos, garantizando integridad y consistencia en las operaciones CRUD del backend.

- Requirements.txt -> El archivo requirements.txt lista todas las dependencias necesarias para ejecutar correctamente el proyecto 7Social, asegurando que el entorno de desarrollo y producción tengan las mismas versiones de librerías instaladas.
Estas librerías abarcan desde frameworks web y procesamiento de datos hasta utilidades de seguridad.

- Schemas.py -> define los modelos de datos Pydantic usados por la API FastAPI de 7Social.
Estos esquemas permiten validar, serializar y estructurar los datos que se envían o reciben entre el frontend, la base de datos y el backend.

- Titulos.json -> El archivo contiene las listas de títulos base que el sistema de recomendación de 7Social utiliza como conjunto inicial de datos para generar recomendaciones emocionales, Cada lista agrupa los ítems disponibles por tipo de contenido —como películas, libros o eventos—, y sirve como punto de partida para mostrar sugerencias al usuario según su emoción o sus calificaciones previas.

- Streamlit_app.py -> El archivo corresponde a la interfaz principal del chatbot emocional de la plataforma 7Social, desarrollado con Streamlit.
Su propósito es ofrecer una experiencia conversacional donde los usuarios puedan pedir recomendaciones , y el sistema responde generando recomendaciones personalizadas de libros, películas o eventos, basadas en la emoción detectada en sus textos.

El flujo general del archivo integra varias capas funcionales:

- 1.Análisis emocional: utiliza bibliotecas de procesamiento de lenguaje natural como spaCy y pysentimiento para detectar emociones a corto plazo a partir de texto. Los resultados incluyen tanto la emoción dominante como las probabilidades de cada categoría emocional (alegría, tristeza, ira, sorpresa, etc.).

- 2.Sistema de recomendación: combina la emoción detectada con las preferencias previas del usuario (almacenadas en archivos JSON) para sugerir contenido relevante.

- Inicialmente, las recomendaciones son aleatorias si no existen recomendaciones para esa emocion, priorizando ítems populares.
Una vez el usuario califica varios elementos, el sistema aplica filtrado colaborativo basado en ítems (Slope one) para afinar las sugerencias.

- 3.Interfaz interactiva: Streamlit presenta una interfaz limpia y dinámica donde:

- El usuario puede escribir un saludo y pedir una recomendacion.

- El chatbot responde mostrando y ofreciendo recomendaciones correspondientes.

- Se permiten calificaciones de los ítems sugeridos para mejorar las recomendaciones futuras.

- 4.Gestión del estado: utiliza st.session_state para conservar información durante la sesión del usuario, como la emoción actual, calificaciones previas y resultados mostrados.

- 5.Integración con APIs externas: se conectan servicios como Google Books (Libros), OMDb (películas) y Ticketmaster (eventos) para obtener datos actualizados y reales de los ítems recomendados (imágenes, sinopsis, títulos, etc.).

- En conjunto, este módulo representa el componente afectivo e interactivo del proyecto, donde la tecnología de procesamiento del lenguaje se combina con la recomendación personalizada para crear una experiencia emocionalmente consciente y adaptativa dentro del ecosistema de 7Social.


**Funcionamiento General**

Usuario inicia sesión en la app web (7Social).

Escribe minimo 3 publicaciónes en la red social

El backend analiza el texto con pysentimiento y spaCy, detectando emociones y contexto.

Se abre el chatbot desde el widget a mano derecha

el chatbot recupera la emocion, el usuario saluda y pide una 
recomentacion , el sistema consulta las APIs externas:

OMDb → películas.

Google Books → libros.

Ticketmaster → eventos.

Se trae la recomendacion con el chatbot

el usuario puede calificar A partir de (≥ 4 estrellas) para que sea tomada en cuenta, se activa el filtrado colaborativo cuando se califican 2 populares con +4 despues de vaciar la lista de populares generando recomendaciones.

El sistema guarda las calificaciones en asociaciones.json.

Las siguientes recomendaciones se ajustan al perfil emocional + patrones de comunidad.

Toda la experiencia se adapta al estado emocional detectado.

**Requerimientos**
El proyecto requiere un entorno de desarrollo basado en Python 3.10 o superior, además de un conjunto de librerías que garantizan la correcta ejecución del sistema backend, el análisis emocional y la conexión con bases de datos.
Estas dependencias están definidas en el archivo requirements.txt, el cual permite una instalación automática mediante el gestor de paquetes pip.
Node.js v16 o superior (recomendado v18).
npm v8+
Git (para clonar / sincronizar el repositorio).

**Requerimientos del sistema**

Para garantizar un funcionamiento óptimo del sistema completo (backend, frontend y chatbot emocional), se recomienda disponer de un entorno con las siguientes especificaciones mínimas y recomendadas:

Tipo de requerimiento	Mínimo	Recomendado

Sistema operativo	Windows 10 / Ubuntu 20.04 / macOS 11	Windows 11 / Ubuntu 22.04 / macOS 13

Procesador (CPU)	Intel Core i3 / AMD Ryzen 3 (2 núcleos)	Intel Core i5 / Ryzen 5 (4 núcleos o más)

Memoria RAM	8 GB	16 GB o más

Espacio en disco	5 GB libres (incluye dependencias y entorno virtual)	10 GB libres o SSD de alta velocidad

Tarjeta gráfica (GPU)	Integrada (opcional)	GPU con soporte CUDA si se usa aceleración de modelos (opcional)

Conexión a internet	Requerida para APIs externas (Google Books, OMDb, Ticketmaster, etc.)	Estable y de banda ancha

Navegador web	Chrome / Edge / Firefox actualizados	Chrome o Edge (última versión estable)

Editor de código recomendado	VS Code	VS Code con extensiones: Python, Prettier, ESLint, React Tools


**Instalacion**
Para la instalación del entorno, se recomienda seguir los pasos descritos a continuación:

**BACKEND**
- 1.Clonar el repositorio desde GitHub:

git clone https://github.com/Aguiar623/7social.git

cd 7social-backend

- 2.Crear y activar un entorno virtual (opcional pero recomendado):

python -m venv venv

venv\Scripts\activate      # En Windows

source venv/bin/activate   # En Linux o macOS

- 3.Instalar todas las dependencias del proyecto:

pip install -r requirements.txt

- 4.Configurar la base de datos:

Editar la variable DATABASE_URL en database.py con los datos de conexión correctos de PostgreSQL:

DATABASE_URL = "postgresql://usuario:contraseña@localhost/nombre_bd"

- 5.Inicializar las tablas y ejecutar el servidor FastAPI:

uvicorn main:app --reload

**FRONTEND**
- 1.Clonar el repositorio desde github y entra en la carpeta del frontend:

git clone https://github.com/Aguiar623/7social.git

cd 7social/7social-frontend 

- 2.Instala dependencias Con npm:

npm install

- 3. Ejecuta la app en modo desarrollo Con npm:

npm run dev

- 4.Por defecto Vite abrirá en http://localhost:5173 (o puerto que indique la consola).

**Importante**
Se debe tener en cuenta que se debe linkear el front con el back, ya que estas versiones son para local pero el front esta siendo utilizado por un servidor en linea , el back si esta solo en local, aunque el repositorio para en linea esta ubicado en la siguiente direccion: https://huggingface.co/spaces/yeferson3256457/7social-back
si quieren tenerlo solo se debe clonar con git clone https://huggingface.co/spaces/yeferson3256457/7social-back.
Para el chatbot streamlit se encuentra en esta direccion ya que se desplego de forma aparte del back en la siguiente direccion: https://huggingface.co/spaces/yeferson3256457/new7chatbot , si se requiere se clona igual que el back ,todo esta montando atraves de contenedores dockers.
en la nube se utiliza una base de datos que esta relacionada con render, la local utiliza postgresql.



