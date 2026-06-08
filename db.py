from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

sqlite_name = "db.sqlite3"
sqlite_url = f"sqlite:///{sqlite_name}"

engine = create_engine(sqlite_url)

def create_all_table():
    # Ejecuta la creación de tablas directamente de forma síncrona y segura
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]