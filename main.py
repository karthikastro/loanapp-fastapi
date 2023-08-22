from fastapi import FastAPI,Depends,HTTPException
import models
from database import engine,SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel,Field
from typing import Optional
from routers.auth import router,get_current_user,get_user_exception
from routers import auth,datahandler,admin,users,loanofficer

app = FastAPI()

models.Base.metadata.create_all(bind = engine)

class Login(BaseModel):
    email : str
    username : str
    first_name : str
    last_name : str
    account_no : int
    ifsc_code : str
    password : str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(loanofficer.router)  