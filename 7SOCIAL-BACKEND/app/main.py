from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import engine, Base, SessionLocal
from models import Post, User
from sqlalchemy.orm import Session, joinedload
from Utils.Analisis_publicaciones import ejecutar_analisis
from schemas import PostCreate, PostResponse, UserCreate, UserResponse
import subprocess
import threading
from Utils.Security import hash_password , verify_password


def run_streamlit():
    subprocess.run(["streamlit", "run", "chatbot_app.py", "--server.port", "8501"])

threading.Thread(target=run_streamlit, daemon=True).start()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)

# Dependencia para la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Esquema Pydantic para crear publicaciones
class PostCreate(BaseModel):
    title: str
    content: str
    user_id: int

# Esquema Pydantic para el usuario
class UserSchema(BaseModel):
    name: str
    username: str
    email: str
    age: int
    password: str

# Esquema Pydantic para el logueo 
class LoginRequest(BaseModel):
    username: str
    password: str

# Endpoint para obtener todas las publicaciones
@app.get("/feed", response_model=list[PostResponse])
def get_feed(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    if not posts:
        return []
    
    result = []
    for post in posts:
        user = db.query(User).filter(User.id == post.user_id).first()
        result.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "user_id": post.user_id,
            "username": user.username if user else "Usuario desconocido"
        })
    return result


# Endpoint para crear una nueva publicación
@app.post("/feed", response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == post.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db_post = Post(title=post.title, content=post.content, user_id=post.user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    post_count = db.query(Post).filter(Post.user_id == post.user_id).count()

    if post_count >= 3:
        print(f"Ejecutando análisis automático para el usuario {user.username}...")
        ejecutar_analisis(post.user_id)
    
    return {
        "id": db_post.id,
        "title": db_post.title,
        "content": db_post.content,
        "user_id": db_post.user_id,
        "username": user.username,
    }


# Endpoint para eliminar las publicaciones
@app.delete("/feed/{post_id}", status_code=204)
def delete_post(post_id: int, user_id: int = Query(...), db: Session = Depends(get_db)):
    # Buscar la publicación por ID
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    
    # Verificar si el usuario que intenta borrar es el dueño
    if post.user_id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta publicación")
    
    # Eliminar la publicación
    db.delete(post)
    db.commit()
    return {"message": "Publicación eliminada"}

# Endpoint para editar las publicaciones
@app.put("/feed/{post_id}", response_model=PostResponse)
def update_post(post_id: int, updated_post: PostCreate, user_id: int = Query(...), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    
    # Verificar si el usuario que intenta editar es el dueño de la publicación
    if post.user_id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar esta publicación")
    
    # Actualiza los campos de la publicación
    post.title = updated_post.title
    post.content = updated_post.content
    db.commit()
    db.refresh(post)
    
    # Obtén el usuario para incluir el `username`
    user = db.query(User).filter(User.id == post.user_id).first()
    
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "user_id": post.user_id,
        "username": user.username if user else "Usuario desconocido",
    }

# Endpoint para el registro
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    #print("Datos recibidos del frontend:", user.model_dump())
    # Verifica si el usuario o correo ya existe
    existing_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario o correo ya está registrado.")
    
    # Crea un nuevo usuario
    new_user = User(
        name=user.name,
        username=user.username,
        email=user.email,
        age=user.age,
        password=hash_password(user.password)  # encritacion de la contraseña 
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Endpoint para el inicio de sesion
@app.post("/login")
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password,user.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas.")
    return {"message": "Inicio de sesión exitoso", "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "age": user.age,
            "username": user.username,
        }}

# detectar cuando el usuario a echo mas de 2 post

@app.get("/user/{user_id}/posts_count")
def check_user_post_count(user_id: int, db: Session = Depends(get_db)):
    count = db.query(Post).filter(Post.user_id == user_id).count()
    return {"count": count}

# devuelve los 3 ultimos post del usuario

@app.get("/user/{user_id}/recent_posts")
def get_recent_posts(user_id: int, db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.user_id == user_id).order_by(Post.id.desc()).limit(3).all()
    return [{"title": p.title, "content": p.content} for p in posts]

#devolver nombre del usuario

@app.get("/user/{user_id}/name")
def get_user_name(user_id: int, db: Session = Depends(get_db)):
    # Obtener el usuario para obtener su nombre
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"name": user.name}