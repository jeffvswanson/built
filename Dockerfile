FROM docker.io/python:3.9.13 AS builder

RUN pip install pipenv

# Default venv directory in project directory
ENV PIPENV_VENV_IN_PROJECT=1

WORKDIR /built

ADD Pipfile.lock Pipfile ./

RUN pipenv sync

RUN pipenv run python -c "import sqlalchemy; print(sqlalchemy.__version__)"

FROM docker.io/python:3.9.13-slim-buster AS runtime

RUN apt-get update && apt-get install -y python3-dev default-libmysqlclient-dev build-essential

WORKDIR /built

COPY --from=builder /built/.venv/ ./venv

COPY ./budgeter ./budgeter

RUN ./venv/bin/python -c "import sqlalchemy; print(sqlalchemy.__version__)"

CMD ["./venv/bin/python", "-m", "flask", "--app", "budgeter", "run", "--host=0.0.0.0"]
