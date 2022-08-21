FROM docker.io/python:3.9.13 AS builder

RUN pip install --user pipenv

# Default venv directory in project directory
ENV PIPENV_VENV_IN_PROJECT=1

ADD Pipfile.lock Pipfile /built/

WORKDIR /built

RUN /root/.local/bin/pipenv sync

RUN /built/.venv/python -c "import sqlalchemy; print(sqlalchemy.__version__)"

FROM docker.io/python:3.9.13 AS runtime

RUN mkdir -v /built/venv

COPY --from=build /built/.venv/ /built/venv

RUN /built/venv/bin/python -c "import sqlalchemy; print(sqlalchemy.__version__)"

WORKDIR /built/

CMD ["flask --app budgeter"]
