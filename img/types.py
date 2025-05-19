from enum import Enum
from pathlib import Path
from typing import Dict, Union

from pydantic import BaseModel, Field, HttpUrl, field_validator


class Language(str, Enum):
    EN = "en"


MediaSource = Union[HttpUrl, Path]


class MediaBase(BaseModel):
    video: MediaSource = Field(
        ..., description="URL or local file path to the media resource"
    )
    language: Language = Field(..., description="Two-letter ISO language code")

    @field_validator("video", mode="before")
    def _coerce_to_path(cls, v):
        # if it looks like a local file path, turn it into Path
        if isinstance(v, str) and not (
            v.startswith("http://") or v.startswith("https://")
        ):
            return Path(v)
        return v


class Styles(MediaBase):
    prompt: str = Field(..., description="Prompt template for this style")


class Configuration(BaseModel):
    styles: Dict[str, Styles]
