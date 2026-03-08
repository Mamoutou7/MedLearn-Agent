from src.healthbot.core.logging import configure_logging
from src.healthbot.cli.main import human_in_the_loop

configure_logging()


if __name__ == "__main__":
    human_in_the_loop()
