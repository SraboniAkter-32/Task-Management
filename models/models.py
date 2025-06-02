from pydantic import BaseModel
from datetime import datetime


class Task(BaseModel):
    title: str
    description: str
    email:str
    status: str
    due_date: str
    created_at: int = int(datetime.timestamp(datetime.now()))


class UserRegister(BaseModel):
    username: str
    password: str
