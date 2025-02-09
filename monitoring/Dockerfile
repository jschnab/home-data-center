# syntax=docker/dockerfile:1
FROM alpine:3.14

ARG USER_NAME=monusr 
ARG USER_HOME=/home/${USER_NAME}

WORKDIR ${USER_HOME}

COPY src .

RUN apk update \
    && apk update \
    && apk add build-base python3-dev linux-headers \
    && adduser -S ${USER_NAME}

USER ${USER_NAME}

RUN --mount=type=cache,target=${USER_HOME}/.cache cd ${USER_HOME} \
    && python3 -m ensurepip \
    && python3 -m venv .venv \
    && source .venv/bin/activate \
    && pip install -U pip setuptools wheel \
    && pip install psutil
