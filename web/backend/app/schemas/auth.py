from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    benutzername: str
    passwort: str


class UserLogin(BaseModel):
    email: EmailStr
    passwort: str


class UserResponse(BaseModel):
    id: int
    email: str
    benutzername: str

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
