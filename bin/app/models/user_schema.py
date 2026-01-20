from pydantic import BaseModel

class RegisterUser(BaseModel):
    _id:int
    username:str
    email:str
    name:str
    password:str


