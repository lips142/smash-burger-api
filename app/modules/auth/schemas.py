from typing import Optional

from pydantic import BaseModel


class LoginData(BaseModel):
    login: Optional[str] = None
    username: Optional[str] = None
    password: str
