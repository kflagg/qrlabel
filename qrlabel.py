#!/usr/bin/env python3

# Import dependencies
import logging
import argparse
import pydantic
import pydantic_settings
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
import qrcode

# Set up logging output.
log = Logger()


# Define and validate settings.
class qrLabelSettings(pydantic_settings.BaseSettings):
    """
    Settings validation class for QRLabel. Settings are read from environment
    variables prefixed with `QRL_`. These can be set in a `.env` file in the
    working directory.

    - default_log_level: The logging level used if not specified at run time.
    """

    default_log_level: int | str = logging.WARNING

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=".env", env_prefix="QRL_"
    )


settings = qrLabelSettings()


# Define and parse command-line arguments.
parser = argparse.ArgumentParser(
    prog="qrlabel",
    description="This is a tool to generate QR code and printable labels.",
)
parser.add_argument(
    "-l",
    "--loglevel",
    default=settings.default_log_level,
    help="level of logging desired; defaults to warning",
)
parser.add_argument(
    "-t",
    "--text",
    default="",
    help="text to encode in QR code",
)
ARGS = vars(parser.parse_args())


class LambdaEvent(pydantic.BaseModel):
    """Class defining the inputs to the lambda."""

    text: str = ARGS.get("text")
    log_level: int | str = ARGS.get("loglevel")


@event_parser(model=LambdaEvent)
# @log.inject_lambda_context
def __run(event: LambdaEvent, context: LambdaContext) -> None:
    # Set logging level.
    log.setLevel(event.log_level)


# Call __run() if being run directly.
if __name__ == "__main__":
    __run({}, None)
