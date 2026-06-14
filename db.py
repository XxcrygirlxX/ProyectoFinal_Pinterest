from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./db.sqlite3"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_all_table():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session