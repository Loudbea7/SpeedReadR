from sqlmodel import SQLModel, Field
from typing import Optional

class Theme(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dark: str = "Dark"
    color: str = "Teal"
    hue: str = "900"