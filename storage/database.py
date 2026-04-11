from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///./codereview.db"
engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine, expire_on_commit=False)
