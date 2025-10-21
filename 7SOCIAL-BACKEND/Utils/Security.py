from passlib.context import CryptContext

# Definir el esquema de encriptacion usando argon2 (más seguro que bcrypt)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Funcion para hashear contraseña
def hash_password(password: str) -> str:
    """
    Recibe una contraseña en texto plano y devuelve el hash seguro.
    """
    return pwd_context.hash(password)

# Funcion para verificar contraseña
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si la contraseña en texto plano coincide con el hash guardado.
    """
    return pwd_context.verify(plain_password, hashed_password)


