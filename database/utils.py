import os


def clear_database():
    database_path = "config/settings.db"
    if os.path.exists(database_path):
        print("Removing previous database...")
        os.remove(database_path)
    else:
        print("Database not found")


def create_db_and_tables():
    from sqlmodel import SQLModel
    from .engine import engine

    SQLModel.metadata.create_all(engine)