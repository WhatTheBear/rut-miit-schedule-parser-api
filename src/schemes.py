from pydantic import BaseModel

class RegisterData(BaseModel):
    userName:str
    login:str
    password:str