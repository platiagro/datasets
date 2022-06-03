# PlatIAgro Datasets

[![.github/workflows/ci.yml](https://github.com/platiagro/datasets/actions/workflows/ci.yml/badge.svg)](https://github.com/platiagro/datasets/actions/workflows/ci.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=platiagro_datasets&metric=alert_status)](https://sonarcloud.io/dashboard?id=platiagro_datasets)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Requirements

You may start the server locally or using a docker container, the requirements for each setup are listed below.

### Local

- [Python 3.8](https://www.python.org/downloads/)

### Docker

- [Docker CE](https://www.docker.com/get-docker)

## Quick Start

Make sure you have all requirements installed on your computer. Then, you may start the server using either a [Docker container](#run-using-docker) or in your [local machine](#run-local).

### Run using Docker

Export these environment variables:

```bash
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minio
export MINIO_SECRET_KEY=minio123
```

(Optional) Start a MinIO instance:

```bash
docker run -d -p 9000:9000 \
  --name minio \
  --env "MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY" \
  --env "MINIO_SECRET_KEY=$MINIO_SECRET_KEY" \
  minio/minio:RELEASE.2018-02-09T22-40-05Z \
  server /data
```

Then, build a docker image that launches the API server:

```bash
docker build -t platiagro/datasets:0.3.1 .
```

Finally, start the API server:

```bash
docker run -it -p 8080:8080 \
  --name datasets \
  --env "MINIO_ENDPOINT=$MINIO_ENDPOINT" \
  --env "MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY" \
  --env "MINIO_SECRET_KEY=$MINIO_SECRET_KEY" \
  platiagro/datasets:0.3.1
```

### Run Local:

Export these environment variables:

```bash
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minio
export MINIO_SECRET_KEY=minio123
```

(Optional) Create a virtualenv:

```bash
virtualenv -p python3 venv
. venv/bin/activate
```

Install Python modules:

```bash
pip install .
```

Then, start the API server:

```bash
uvicorn datasets.api:app
```

Arguments:

```bash
usage: uvicorn datasets.api:app [-h] [--host TEXT] [--port INTEGER] [--workers INTEGER]

Datasets API

optional arguments:
  -h, --help         show this help message and exit
  --host TEXT        Bind socket to this host (default: 127.0.0.1)
  --port INTEGER     Port for HTTP server (default: 8000)
  --workers INTEGER  Number of worker processes.

environment variables:
  ENABLE_CORS          whether to enable CORS headers for all responses.
```

## Testing

Install the testing requirements:

```bash
pip install .[testing]
```

Export these environment variables:

```bash
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minio
export MINIO_SECRET_KEY=minio123
```

Use the following command to run all tests:

```bash
pytest
```

Use the following command to run lint:

```bash
flake8 --max-line-length 127 datasets/
```

## API

See the [PlatIAgro Datasets API doc](https://platiagro.github.io/datasets/) for API specification.
