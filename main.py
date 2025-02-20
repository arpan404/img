from img.config import Config
from img.img import Img

def main():
    config = Config("config.json")
    config.load()
    img = Img()
    # img.generate(config=config.get_style("style1"))
    img.generate(config=config.get_story("story1"))

if __name__ == "__main__":
    main()
