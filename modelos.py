from sqlmodel import SQLModel, Field
from typing import Optional

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True)
    password: str
    bio: str = Field(default="Diseñando mi tablero de sueños en Fyntasy")

class Pin(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    descripcion: str
    source: str
    categoria: str = Field(default="chill")
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    username_autor: str = Field(default="Fyntasy_Girl")
    es_publico: bool = Field(default=True)
    reportado: bool = Field(default=False)

class Comentario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    texto: str
    pin_id: int = Field(foreign_key="pin.id")
    usuario_id: int = Field(foreign_key="usuario.id")
    username_autor: str

# NUEVA TABLA PARA MODERACIÓN COMUNITARIA
class Reporte(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pin_id: int = Field(foreign_key="pin.id")
    usuario_id: int = Field(foreign_key="usuario.id")