FROM --platform=linux/x86_64 public.ecr.aws/lambda/python:3.14-x86_64

# Install poetry and dependencies.
RUN yum install gcc libxslt-devel libxml2-devel -y
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN /root/.local/bin/poetry config virtualenvs.create false

# Set up poetry environment.
COPY pyproject.toml .
COPY poetry.lock .
RUN /root/.local/bin/poetry install --only main

# Set up entry point.
COPY qrlabel.py ${LAMBDA_TASK_ROOT}
CMD [ "qrlabel.__run" ]