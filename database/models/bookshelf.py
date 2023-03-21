from sqlmodel import SQLModel, Field
from typing import Optional


class Bookshelf(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = "Readme.txt"
    hash: str = ""
    type: str = "text/plain"
    # length: int = 0
    indx: int = 0
    progress: int = 0