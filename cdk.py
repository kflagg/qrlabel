#!/usr/bin/env python3
import os
import aws_cdk

from aws_cdk import (
    Stack,
    Duration,
    aws_lambda,
    aws_apigateway,
)
from constructs import Construct


class QrlabelStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The lambda.
        qrl_lambda = aws_lambda.Function(
            self,
            "QRL",
            description="QR Label Generator",
            code=aws_lambda.Code.from_asset_image(directory="."),
            handler=aws_lambda.Handler.FROM_IMAGE,
            runtime=aws_lambda.Runtime.FROM_IMAGE,
            architecture=aws_lambda.Architecture.X86_64,
            timeout=Duration.minutes(1),
            memory_size=128,
        )

        # The QR label API.
        qrlabel_api = aws_apigateway.LambdaRestApi(
            self,
            "QRLabel",
            description="QR Image API",
            handler=qrl_lambda,
            proxy=False,
            deploy=True,
        )

        # Root is the label resource.
        qrlabel_api.root.add_method(
            "GET",
            request_parameters={
                "method.request.querystring.text": True,
                "method.request.querystring.upper": False,
                "method.request.querystring.lower": False,
                "method.request.querystring.error_correction": False,
                "method.request.querystring.box_size": False,
                "method.request.querystring.border": False,
                "method.request.querystring.fill_color": False,
                "method.request.querystring.back_color": False,
                "method.request.querystring.encoding": False,
                "method.request.querystring.method": False,
                "method.request.querystring.xml_declaration": False,
            },
        )

        # Add the image resource.
        qrimage_api = qrlabel_api.root.add_resource("image")
        qrimage_api.add_method(
            "GET",
            request_parameters={
                "method.request.querystring.text": True,
                "method.request.querystring.error_correction": False,
                "method.request.querystring.box_size": False,
                "method.request.querystring.border": False,
                "method.request.querystring.fill_color": False,
                "method.request.querystring.back_color": False,
                "method.request.querystring.encoding": False,
                "method.request.querystring.method": False,
                "method.request.querystring.xml_declaration": False,
            },
        )


app = aws_cdk.App()
QrlabelStack(app, "QRLabelStack")

app.synth()
