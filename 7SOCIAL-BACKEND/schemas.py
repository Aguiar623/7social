from pydantic import BaseModel, EmailStr

# Modelo para crear o actualizar publicaciones
class PostCreate(BaseModel):
    title: str
    content: str
    user_id: int  # Relaciona la publicacion con un usuario

# Modelo para devolver publicaciones en las respuestas
class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int  # Incluye el ID del usuario
    username: str  # incluir el nombre de usuario para mostrarlo directamente

    class Config:
        from_attributes = True  # Habilita la conversion de objetos ORM a Pydantic

# Modelos para el registro
class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    age: int
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    username: str
    email: EmailStr
    age: int

    class Config:
        from_attributes = True
