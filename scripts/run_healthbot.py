from healthbot.cli.main import human_in_the_loop
from healthbot.core.logging import configure_logging

configure_logging()


if __name__ == "__main__":
    human_in_the_loop()
