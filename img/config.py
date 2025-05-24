"""
This module handles the configuration for the image generation process.
"""

import json
from functools import lru_cache
from pathlib import Path

from img.types import Configuration, Styles


class Config:
    __slots__ = ("_path", "_config")

    def __init__(self, path: str | Path = Path.cwd() / "config.json"):
        self._path = Path(path)
        if not self._path.is_absolute():
            self._path = Path.cwd() / self._path
        if not self._path.is_file():
            raise FileNotFoundError(f"Configuration file not found: {self._path}")
        self._config = self._load()

    def _load(self) -> Configuration:
        """Read and validate the JSON config file."""
        with self._path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return Configuration.model_validate(data)

    @lru_cache(maxsize=1)
    def get_style(self, variant: str) -> Styles:
        """
        Retrieve a specific style variant.
        Raises KeyError if the variant is not defined.
        """
        try:
            return self._config.styles[variant]
        except KeyError as e:
            raise KeyError(f"Style variant '{variant}' not found") from e
