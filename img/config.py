import json
import os


class Config:
    config_data = None

    def __int__(self, path: str = os.path.join(os.getcwd(), 'config.json')):
        self.path = path
        
    def load(self):
        """
        Loads the configuration file and return the save and return the config data
        """
        if self.config_data is None:
            with open(self.path, 'r') as file:
                self.config_data = json.load(file)
        return self.config_data

    def style(self, variant: str) -> dict:
        """
        Returns the style of the content, which indicates the style of the content, including the voice, prompt, and other parameters
        """
        return self.config_data[variant]
