from passlib.context import CryptContext

# Definir el esquema de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Función para hashear
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Función para verificar contraseña
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
