#!/usr/bin/env python3
import os
import aws_cdk

from aws_cdk import (
    Stack,
    Duration,
    aws_lambda,
    aws_apigatewayv2,
    aws_apigatewayv2_integrations,
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
        qrl_api = aws_apigatewayv2.HttpApi(
            self,
            "QRLabel",
            description="QR Label API",
        )

        # Add the label resource.
        qrlabel_api = qrl_api.add_routes(
            path="/",
            methods=[aws_apigatewayv2.HttpMethod.GET],
            integration=aws_apigatewayv2_integrations.HttpLambdaIntegration(
                "QRL",
                handler=qrl_lambda,
            ),
        )


app = aws_cdk.App()
QrlabelStack(app, "QRLabelStack")

app.synth()
