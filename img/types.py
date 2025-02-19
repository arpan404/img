from pydantic import BaseModel
from typing import Dict


"""
For Configuration file
"""


class Styles(BaseModel):
    prompt: str
    video: str
    language: str


class Stories(BaseModel):
    story: str
    video: str
    language: str


# type for Config file and the content of the config file, same as the
class Configuration(BaseModel):
    styles: Dict[str, Styles]
    stories: Dict[str, Stories]


"""
For Img class
"""
