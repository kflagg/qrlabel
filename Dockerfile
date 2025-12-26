FROM public.ecr.aws/lambda/python:3.11-x86_64

# Install poetry and dependencies.
RUN yum install gcc libxslt-devel libxml2-devel -y
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN /root/.local/bin/poetry config virtualenvs.create false

# Set up poetry environment.
COPY pyproject.toml ${LAMBDA_TASK_ROOT}
COPY poetry.lock ${LAMBDA_TASK_ROOT}
COPY README.md ${LAMBDA_TASK_ROOT}
COPY qrlabel.py ${LAMBDA_TASK_ROOT}
RUN /root/.local/bin/poetry install --only main

# Set up entry point.
CMD [ "qrlabel.__run" ]