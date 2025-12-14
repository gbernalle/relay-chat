from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@localhost/auth_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserList(BaseModel):
    username: str

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserAuth(BaseModel):
    username: str
    password: str

@app.get("/users", response_model=List[UserList])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users


@app.post("/register")
def register(user: UserAuth, db: Session = Depends(get_db)):

    username_normalized = user.username.lower()

    db_user = (
        db.query(UserModel).filter(UserModel.username == username_normalized).first()
    )
    if db_user:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    hashed_pw = pwd_context.hash(user.password)
    new_user = UserModel(username=username_normalized, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    return {"message": "Usuário criado com sucesso"}


@app.post("/login")
def login(user: UserAuth, db: Session = Depends(get_db)):
    
    username_normalized = user.username.lower()
    
    db_user = (
        db.query(UserModel).filter(UserModel.username == username_normalized).first()
    )

    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    return {"username": db_user.username, "user_id": db_user.id}
