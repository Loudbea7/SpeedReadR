from sqlmodel import Session, select
from ..engine import engine
from ..models.active import Active
from typing import List


class ActiveDAO:
    def __init__(self) -> None:
        if not self.active:
            self.create_initial_active()

    def read_active(self):
        with Session(engine) as db:
            active = db.exec(select(Active)).all()

            return active
    
    def get_active(self):
        with Session(engine) as db:
            active = db.exec(select(Active)).all()[0]

            return active

    @property
    def active(self) -> List[Active]:
        return self.read_active()

    def create_active(self):
        active = Active()
        with Session(engine) as db:
            db.add(active)
            db.commit()
            db.refresh(active)
            return active

    def update_active(
        self,
        setting_active=None,
        path=None,
        book=None,
        total=None
        ):
        with Session(engine) as db:
            # active = db.get(Active)
            active = db.exec(select(Active)).all()[0]
            if active:
                if setting_active is not None:
                    active.setting_active = setting_active
                if path is not None:
                    active.path = path
                if book is not None:
                    active.book = book
                if total is not None:
                    active.total = total
                db.add(active)
                db.commit()
                db.refresh(active)
                return active
            else:
                raise ValueError(f"Can't write config")

    def delete_active(self, slot: int):
        with Session(engine) as db:
            active = db.get(Active, slot)
            if active:
                db.delete(active)
                db.commit()

    def create_initial_active(self):
        self.create_active()