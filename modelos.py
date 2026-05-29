from sqlmodel import Field, SQLModel

class Pin(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    source: str 
    titulo: str
    es_publico: bool

class PinCreate(SQLModel):
    source: str
    titulo: str
    es_publico: bool

class Comentario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    texto: str
    pin_id: int = Field(foreign_key="pin.id")