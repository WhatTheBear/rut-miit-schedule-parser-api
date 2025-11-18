from pydantic import BaseModel


class RegisterData(BaseModel):
    userName: str
    login: str
    password: str


# class EventInfo(BaseModel):
#     subject: str
#     type: str
#     start: str
#     end: str
#     slot: str
#     audience: list
#     groups: list
#     lecturers: list
