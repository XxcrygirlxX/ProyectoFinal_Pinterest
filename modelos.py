from pydantic import BaseModel, EmailStr, Field
from sqlmodel import SQLModel, Field as SQLField
from typing import Optional

class Usuario(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    email: str = SQLField(unique=True, index=True) 
    password: Optional[str] = SQLField(default=None, nullable=True)
    google_id: Optional[str] = None
    # Nuevos campos para el Perfil
    nombre: Optional[str] = None
    biografia: Optional[str] = None
    avatar_url: Optional[str] = None

class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class Pin(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    source: str # Aquí guardaremos la URL/Ruta de la imagen subida
    titulo: str
    es_publico: bool = SQLField(default=True)  
    reportado: bool = SQLField(default=False)
    usuario_id: int = SQLField(foreign_key="usuario.id", default=1) # Quién lo subió

class Comentario(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    texto: str
    pin_id: int = SQLField(foreign_key="pin.id")
    usuario_id: Optional[int] = SQLField(foreign_key="usuario.id", default=None)

# NUEVO: Carpetas / Tableros
class Tablero(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    nombre: str
    usuario_id: int = SQLField(foreign_key="usuario.id")

# NUEVO: Guardar Pines
class PinGuardado(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    pin_id: int = SQLField(foreign_key="pin.id")
    tablero_id: int = SQLField(foreign_key="tablero.id")
    usuario_id: int = SQLField(foreign_key="usuario.id")