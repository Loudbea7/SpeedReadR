from sqlmodel import SQLModel, Field
from typing import Optional
import os

# def_path = os.path.abspath("./Books/")
def_path = "Books/"
def_path = os.path.join(def_path, '')

class Active(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    setting_active: str = "s1"
    path: str = def_path
    book: str = "Readme.txt"
    total: int = 0