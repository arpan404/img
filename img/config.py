import json
import os
from pydantic import BaseModel
from typing import Dict

class GenerationStyle(BaseModel):
    prompt: str
    video: str
    language: str

class Stories(BaseModel):
    story: str
    video: str
    language: str

# type for Config file and the content of the config file, same as the
class Configuration(BaseModel):
    styles: Dict[str, GenerationStyle]
    stories: Dict[str, Stories]


class Config:
    config_data = None

    def __init__(self, path: str = os.path.join(os.getcwd(), "config.json")):
        # set the absolute path of the config file
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file not found: {path}")
        self.path = path

    def load(self):
        """
        Loads the configuration file and return the save and return the config data
        """
        if self.config_data is None:
            with open(self.path, "r") as file:
                self.config_data = Configuration.model_validate(json.load(file))
        print(self.config_data)
        return self.config_data

    def get_style(self, variant: str) -> GenerationStyle:
        """
        Returns the style of the content, which indicates the style of the content, including the voice, prompt, and other parameters
        """
        return self.config_data.styles[variant]
    
    def get_story(self, variant: str) -> Stories:
        """
        Returns the story of the content, which indicates the story of the content, including the story, video, and other parameters
        """
        return self.config_data.stories[variant]
