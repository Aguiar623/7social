from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker , declarative_base

# URL de conexión a PostgreSQL
DATABASE_URL = "postgresql://postgres:dunklow5566@localhost/postgres"

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("conexion ok.")
except Exception as e:
    print("error de conexion:" , e)
# Crear una sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative Base
Base = declarative_base()