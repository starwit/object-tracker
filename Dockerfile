FROM python:3.12-slim AS build

ADD "https://drive.google.com/uc?id=1Kkx2zW89jq_NETu4u42CFZTMVD5Hwm6e" /code/osnet_x0_25_msmt17.pt

RUN apt update && apt install --no-install-recommends -y \
    curl \
    git \
    build-essential

ARG POETRY_VERSION
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="${POETRY_HOME}/bin:${PATH}"

# Copy only files that are necessary to install dependencies
COPY poetry.lock poetry.toml pyproject.toml /code/

WORKDIR /code
RUN poetry install
    
# Copy the rest of the project
COPY . /code/


### Main artifact / deliverable image

FROM python:3.12-slim
RUN apt update && apt install --no-install-recommends -y \
    libglib2.0-0 \
    libgl1 \
    libturbojpeg0

COPY --from=build /code /code
WORKDIR /code
ENV PATH="/code/.venv/bin:$PATH"
CMD [ "python", "main.py" ]