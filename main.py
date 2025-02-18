from img.config import Config
from img.img import Img
import uuid

def main():
    config = Config("config.json")
    config.load()
    style = config.style("style2")
    content_id = str(uuid.uuid4())
    img = Img(style, content_id)
    img.generate()

if __name__ == "__main__":
    main()
