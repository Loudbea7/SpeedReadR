from sqlmodel import create_engine
from .models.settings import Settings
from .models.bookshelf import Bookshelf
from .models.active import Active
from .models.themes import Theme

sqlite_file_name = "config/settings.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)