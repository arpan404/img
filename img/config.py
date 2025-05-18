import json
import os

from img.types import Configuration, Stories, Styles


class Config:
    config_data = None

    def __init__(self, path: str = os.path.join(os.getcwd(), "config.json")):
        # set the absolute path of the config file
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file not found: {path}")
        self.path = path

    def load(self) -> None:
        """
        Loads the configuration file and return the save and return the config data
        """
        if self.config_data is None:
            with open(self.path, "r") as file:
                self.config_data = Configuration.model_validate(json.load(file))

    def get_style(self, variant: str) -> Styles:
        """
        Returns the style of the content, which indicates the style of the content, including the voice, prompt, and other parameters
        """
        return self.config_data.styles[variant]

    def get_story(self, variant: str) -> Stories:
        """
        Returns the story of the content, which indicates the story of the content, including the story, video, and other parameters
        """
        return self.config_data.stories[variant]
