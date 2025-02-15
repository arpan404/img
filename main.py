from  img.config import Config

def main():
    config = Config("config.json")
    config.load()
    print(config.style('style1'))
    
if __name__ == "__main__":
    main()