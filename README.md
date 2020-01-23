# PlatIAgro Datasets

[![Build Status](https://travis-ci.org/platiagro/datasets.svg)](https://travis-ci.org/platiagro/datasets)
[![codecov](https://codecov.io/gh/platiagro/datasets/graph/badge.svg)](https://codecov.io/gh/platiagro/datasets)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)
[![Gitter](https://badges.gitter.im/platiagro/community.svg)](https://gitter.im/platiagro/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Known Vulnerabilities](https://snyk.io/test/github/platiagro/dataset-store/master/badge.svg?targetFile=package.json)](https://snyk.io/test/github/platiagro/dataset-store/master/?targetFile=package.json)

## Requirements

You may start the server locally or using a docker container, the requirements for each setup are listed below.

### Local

- [Python 3.6](https://www.python.org/downloads/)
- [MinIO](https://docs.min.io/docs/minio-quickstart-guide.html)

### Docker

- [Docker CE](https://www.docker.com/get-docker)

## Quick Start

Make sure you have all requirements installed on your computer. Then, you may start the server using either a [Docker container](#run-using-docker) or in your [local machine](#run-local).

### Run using Docker

Export these environment variables:

```bash
export MINIO_ENDPOINT=minio:9000
export MINIO_ACCESS_KEY=some-access-key
export MINIO_SECRET_KEY=some-secret-key
```

Create a docker network:
```bash
docker network create dev
```

Start MinIO:

```bash
docker run -d -p 9000:9000 \
  --name minio \
  --env "MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY" \
  --env "MINIO_SECRET_KEY=$MINIO_SECRET_KEY" \
  --network dev \
  minio/minio server /data
```

Then, build a docker image that launches the API server:

```bash
docker build -t platiagro/datasets:0.0.1 .
```

Finally, start the API server:

```bash
docker run -it -p 8080:8080 \
  --name datasets \
  --env "MINIO_ENDPOINT=$MINIO_ENDPOINT" \
  --env "MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY" \
  --env "MINIO_SECRET_KEY=$MINIO_SECRET_KEY" \
  --network dev \
  platiagro/datasets:0.0.1
```

### Run Local:

Export these environment variables:

```bash
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=some-access-key
export MINIO_SECRET_KEY=some-secret-key
```

Download MinIO binaries from https://docs.min.io/docs/minio-quickstart-guide.html, and follow the instructions to start the server.

Install Python modules:


```bash
pip install .
```

Then, start the API server:

```bash
python -m datasets.api
```

## Testing

Install the testing requirements:

```bash
pip install .[testing]
```

Use the following command to run all tests:

```bash
pytest
```

## API

TODO