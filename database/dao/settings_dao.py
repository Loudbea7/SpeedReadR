from sqlmodel import Session, select
from ..engine import engine
from ..models.settings import Settings
from typing import List


class SettingsDAO:
    def __init__(self) -> None:
        if not self.settings:
            self.create_initial_settings()

    def read_settings(self):
        with Session(engine) as db:
            settings = db.exec(select(Settings)).all()

            return settings
    
    def get_setting(self, slot):
        with Session(engine) as db:
            settings = db.exec(select(Settings).where(Settings.active == slot )).all()[0]

            return settings

    @property
    def settings(self) -> List[Settings]:
        return self.read_settings()

    def create_settings(self, active: str):
        s1 = Settings(active=active)
        with Session(engine) as db:
            db.add(s1)
            db.commit()
            db.refresh(s1)
            return s1
    
    def update_settings(
        self,
        slot,
        active=None,
        bg_text_size=None,
        reader_text_size=None,
        wpm=None,
        accel=None,
        pointer=None,
        l_w_delay=None,
        dot_delay=None,
        comma_delay=None,
        progress_bar=None,
        blink_toggle=None,
        blink_interval=None,
        blink_delay=None,
        blink_color=None,
        blink_fade_toggle=None,
        blink_fade=None,
    ):
        with Session(engine) as db:
            # settings = db.get(Settings, slot)
            settings = db.exec(select(Settings).where(Settings.active == slot )).all()[0]
            print("SAVING SETTINGS: ", settings)
            if settings:
                if active is not None:
                    settings.active = active
                if bg_text_size is not None:
                    settings.bg_text_size = bg_text_size
                if reader_text_size is not None:
                    settings.reader_text_size = reader_text_size
                if wpm is not None:
                    settings.wpm = wpm
                if accel is not None:
                    settings.accel = accel
                if pointer is not None:
                    settings.pointer = pointer
                if l_w_delay is not None:
                    settings.l_w_delay = l_w_delay
                if dot_delay is not None:
                    settings.dot_delay = dot_delay
                if comma_delay is not None:
                    settings.comma_delay = comma_delay
                if progress_bar is not None:
                    settings.progress_bar = progress_bar
                if blink_toggle is not None:
                    settings.blink_toggle = blink_toggle
                if blink_interval is not None:
                    settings.blink_interval = blink_interval
                if blink_delay is not None:
                    settings.blink_delay = blink_delay
                if blink_color is not None:
                    settings.blink_color = blink_color
                if blink_fade_toggle is not None:
                    settings.blink_fade_toggle = blink_fade_toggle
                if blink_fade is not None:
                    settings.blink_fade = blink_fade
                print("All setted")
                db.add(settings)
                print("All added")
                db.commit()
                print("All comited")
                db.refresh(settings)
                print("All refreshed")
                return settings
            else:
                raise ValueError(f"Config {slot} not found.")

    def delete_settings(self, slot: int):
        with Session(engine) as db:
            settings = db.get(Settings, slot)
            if settings:
                db.delete(settings)
                db.commit()

    def create_initial_settings(self):
        self.create_settings("s1")
        self.create_settings("s2")
        self.create_settings("s3")
