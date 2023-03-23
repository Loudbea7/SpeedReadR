from sqlmodel import Session, select
from ..engine import engine
from ..models.themes import Theme
from typing import List


class ThemeDAO:
    def __init__(self) -> None:
        if not self.theme:
            self.create_initial_theme()

    def read_theme(self):
        with Session(engine) as db:
            theme = db.exec(select(Theme)).all()[0]

            return theme

    @property
    def theme(self) -> List[Theme]:
        return self.read_theme()

    def create_theme(self):
        theme = Theme()
        with Session(engine) as db:
            db.add(theme)
            db.commit()
            db.refresh(theme)
            return theme

    def update_theme(
        self,
        dark=None,
        color=None,
        hue=None,
    ):
        with Session(engine) as db:
            theme = db.get(Theme)
            if theme:
                if dark is not None:
                    theme.dark = dark
                if color is not None:
                    theme.color = color
                if hue is not None:
                    theme.hue = hue
                db.add(theme)
                db.commit()
                db.refresh(theme)
                return theme
            else:
                raise ValueError(f"Can't write config")

    def delete_theme(self, slot: int):
        with Session(engine) as db:
            theme = db.get(Theme, slot)
            if theme:
                db.delete(theme)
                db.commit()

    def create_initial_theme(self):
        self.create_theme()
