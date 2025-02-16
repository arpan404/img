from img.config import Config
from img.content import Content


def main():
    config = Config("config.json")
    config.load()
    style = config.style("style1")
    content = Content()
    content.generate(style)


if __name__ == "__main__":
    main()
