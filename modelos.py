from pydantic import BaseModel, EmailStr, Field
from sqlmodel import SQLModel, Field as SQLField, AutoString
from typing import Optional

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # CORRECCIÓN AQUÍ: Forzamos a SQLAlchemy a tratar EmailStr como un String/Texto
    email: str = Field(unique=True, index=True) 
    password: str
    google_id: Optional[str] = None

class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class Pin(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    source: str 
    titulo: str
    es_publico: bool
    reportado: bool = False

class PinCreate(SQLModel):
    source: str
    titulo: str
    es_publico: bool

class Comentario(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    texto: str
    pin_id: int = SQLField(foreign_key="pin.id")