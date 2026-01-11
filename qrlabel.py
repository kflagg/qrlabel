# Import dependencies
import logging
import pydantic
import pydantic_settings
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.parser import event_parser
import qrcode.constants
import qrcode.image.svg
import html

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


class QueryStringParams(pydantic.BaseModel):
    """Class defining the inputs to the API."""

    text: str  # Text to encode.
    upper: str = ""  # Text above the image.
    lower: str = ""  # Text below the image.
    label: bool = True  # Generate a full label. If false, returns only the QR SVG.
    error_correction: int = qrcode.constants.ERROR_CORRECT_L  # Error correction level.
    box_size: int = 10  # Size of the QR code box.
    border: int = 4  # Border size around the QR code.
    fill_color: str | tuple[int, int, int] = "black"  # Color of the QR code.
    back_color: str | tuple[int, int, int] = "white"  # Background color of the QR code.
    encoding: str | None = "unicode"  # Text encoding of the SVG.
    method: str | None = None  # Method to use for SVG generation.
    xml_declaration: bool | None = None  # Include XML declaration in the SVG.
    default_namespace: str | None = None  # Default namespace for the SVG.
    short_empty_elements: bool = True  # Use short empty elements in the SVG.
    log_level: int | str = settings.default_log_level  # Logging level.


class LambdaEvent(pydantic.BaseModel):
    """Class defining the event passed to the lambda."""

    version: float
    routeKey: str
    rawPath: str
    rawQueryString: str | None
    headers: dict | None
    queryStringParameters: QueryStringParams
    requestContext: dict | None
    isBase64Encoded: bool


@event_parser(model=LambdaEvent)
@log.inject_lambda_context
def __run(event: LambdaEvent, context: LambdaContext) -> str:
    # Set logging level.
    log.setLevel(event.queryStringParameters.log_level)

    # Generate QR code image.
    qr = qrcode.QRCode(
        error_correction=event.queryStringParameters.error_correction,
        box_size=event.queryStringParameters.box_size,
        border=event.queryStringParameters.border,
        image_factory=qrcode.image.svg.SvgPathImage,
    )
    qr.add_data(event.queryStringParameters.text)
    qr.make(fit=True)
    svg = qr.make_image(
        fill_color=event.queryStringParameters.fill_color,
        back_color=event.queryStringParameters.back_color,
    ).to_string(
        encoding=event.queryStringParameters.encoding,
        method=event.queryStringParameters.method,
        xml_declaration=event.queryStringParameters.xml_declaration,
        default_namespace=event.queryStringParameters.default_namespace,
        short_empty_elements=event.queryStringParameters.short_empty_elements,
    )

    if event.queryStringParameters.label:
        log.debug(event.queryStringParameters.upper)
        upper = html.escape(event.queryStringParameters.upper).replace("\\n", "<br />")
        log.debug(upper)
        log.debug(event.queryStringParameters.lower)
        lower = html.escape(event.queryStringParameters.lower).replace("\\n", "<br />")
        log.debug(lower)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "isBase64Encoded": False,
            "body": f"""
                <head><title>{html.escape(event.queryStringParameters.text)}</title></head>
                <body>
                    <div id='label' style='text-align: center; width: 2.5in;'>
                        <p id='upper'>{upper}</p>
                        {svg}
                        <p id='lower'>{lower}</p>
                    </div>
                </body>""",
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "image/svg+xml"},
        "isBase64Encoded": False,
        "body": svg,
    }
