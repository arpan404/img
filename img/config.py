import json
import os


class Config:
    config_data = None

    def __int__(self, path: str = os.path.join(os.getcwd(), 'config.json')):
        self.path = path

    # load the config file from the path and return the config data
    # donot load the config file again if it is already loaded
    def load(self):
        if self.config_data is None:
            with open(self.path, 'r') as file:
                self.config_data = json.load(file)
        return self.config_data

    # style is what defines the style of the content, including the voice, prompt, and other parameters
    def style(self, variant: str) -> dict:
        return self.config_data[variant]
