from sqlmodel import SQLModel, Field
from typing import Optional


class Settings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    active: str
    bg_text_size: int = 18
    reader_text_size: int = 40
    wpm: int = 450
    accel: int = 5
    pointer: bool = True
    l_w_delay: int = 50
    dot_delay: int = 10
    comma_delay: int = 10
    progress_bar: int = True
    blink_toggle: bool = True
    blink_interval: int = 5
    blink_delay: int = 500
    blink_color: str = "[0.62, 0.15, 0.04, 1]"
    blink_fade_toggle: bool = True
    blink_fade: int = 30
    create_readme: bool = True
