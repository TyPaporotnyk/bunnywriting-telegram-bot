FROM python:3.12-slim as python-base

ENV POETRY_VERSION=1.7.1
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-ven

ENV POETRY_CACHE_DIR=/opt/.cache

RUN python3 -m venv $POETRY_VENV && \
    $POETRY_VENV/bin/pip install -U pip setuptools && \
    $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

FROM python-base as poetry-base
COPY --from=python-base ${POETRY_VENV} ${POETRY_VENV}

FROM python-base as app

ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN python -m venv .venv && \
    .venv/bin/pip install -U pip && \
    .venv/bin/pip install poetry==${POETRY_VERSION} && \
    poetry install --no-interaction --no-cache --no-root

COPY . ./
