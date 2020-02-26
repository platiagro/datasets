# PlatIAgro Datasets

[![Build Status](https://travis-ci.org/platiagro/datasets.svg)](https://travis-ci.org/platiagro/datasets)
[![codecov](https://codecov.io/gh/platiagro/datasets/graph/badge.svg)](https://codecov.io/gh/platiagro/datasets)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Gitter](https://badges.gitter.im/platiagro/community.svg)](https://gitter.im/platiagro/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Known Vulnerabilities](https://snyk.io/test/github/platiagro/dataset-store/master/badge.svg?targetFile=package.json)](https://snyk.io/test/github/platiagro/dataset-store/master/?targetFile=package.json)

## Requirements

You may start the server locally or using a docker container, the requirements for each setup are listed below.

### Local

- [Python 3.6](https://www.python.org/downloads/)

### Docker

- [Docker CE](https://www.docker.com/get-docker)

## Quick Start

Make sure you have all requirements installed on your computer. Then, you may start the server using either a [Docker container](#run-using-docker) or in your [local machine](#run-local).

### Run using Docker

Export these environment variables:

```bash
export MINIO_ENDPOINT=play.min.io
export MINIO_ACCESS_KEY=Q3AM3UQ867SPQQA43P2F
export MINIO_SECRET_KEY=zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG
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
  platiagro/datasets:0.0.1
```

### Run Local:

Export these environment variables:

```bash
export MINIO_ENDPOINT=play.min.io
export MINIO_ACCESS_KEY=Q3AM3UQ867SPQQA43P2F
export MINIO_SECRET_KEY=zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG
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
python -m datasets.api
```

## Testing

Install the testing requirements:

```bash
pip install .[testing]
```

Export these environment variables:

```bash
export MINIO_ENDPOINT=play.min.io
export MINIO_ACCESS_KEY=Q3AM3UQ867SPQQA43P2F
export MINIO_SECRET_KEY=zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG
```

Use the following command to run all tests:

```bash
pytest
```

## API

API Reference with examples.

### Datasets

**Lists datasets:** <br>
method: GET <br>
url: /datasets

```bash
curl -X GET \
  http://localhost:8080/datasets
```

Expected Output:

```bash
[{"filename":"iris.data","name":"c568a929-91a3-4b84-9ef9-f1887518abb4"}]
```

**Uploads a dataset:** <br>
method: POST <br>
url: /datasets

With feature types:

```bash
curl -X POST \
  http://localhost:8080/datasets \
  -H "Content-Type: multipart/form-data" \
  -F file=@iris.data \
  -F featuretypes=@featuretypes.txt
```

Without feature types:

```bash
curl -X POST \
  http://localhost:8080/datasets \
  -H "Content-Type: multipart/form-data" \
  -F file=@iris.data
```

Expected Output:

```bash
{"columns":[{"featuretype":"Numerical","name":"col0"},{"featuretype":"Numerical","name":"col1"},{"featuretype":"Numerical","name":"col2"},{"featuretype":"Numerical","name":"col3"},{"featuretype":"Categorical","name":"col4"}],"filename":"iris.data","name":"c568a929-91a3-4b84-9ef9-f1887518abb4","url":"http://play.min.io/anonymous/datasets/c568a929-91a3-4b84-9ef9-f1887518abb4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=Q3AM3UQ867SPQQA43P2F%2F20200131%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20200131T145838Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=07627aa6d4369cb00edfca5c65d87d0e263622944a7728889b131979263b8cc6"}
```

**Details a dataset** <br>
method: GET <br>
url: /datasets/:dataset

```bash
curl -X GET \
  http://localhost:8080/datasets/c568a929-91a3-4b84-9ef9-f1887518abb4
```

Expected Output:

```bash
{"columns":[{"featuretype":"Numerical","name":"col0"},{"featuretype":"Numerical","name":"col1"},{"featuretype":"Numerical","name":"col2"},{"featuretype":"Numerical","name":"col3"},{"featuretype":"Categorical","name":"col4"}],"filename":"iris.data","name":"c568a929-91a3-4b84-9ef9-f1887518abb4","url":"http://play.min.io/anonymous/datasets/c568a929-91a3-4b84-9ef9-f1887518abb4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=Q3AM3UQ867SPQQA43P2F%2F20200131%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20200131T145838Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=07627aa6d4369cb00edfca5c65d87d0e263622944a7728889b131979263b8cc6"}
```

### Columns

**Lists columns and feature types** <br>
method: GET <br>
url: /datasets/:dataset/columns

```bash
curl -X GET \
  http://localhost:8080/datasets/c568a929-91a3-4b84-9ef9-f1887518abb4/columns
```

Expected Output:

```bash
[{"featuretype":"Numerical","name":"col0"},{"featuretype":"Numerical","name":"col1"},{"featuretype":"Numerical","name":"col2"},{"featuretype":"Numerical","name":"col3"},{"featuretype":"Categorical","name":"col4"}]
```

**Updates a column:** <br>
method: PATCH <br>
url: /datasets/:dataset/columns/:column

```bash
curl -X PATCH \
 http://localhost:8080/datasets/c568a929-91a3-4b84-9ef9-f1887518abb4/columns/col0 \
  -H 'Content-Type: application/json' \
  -d '{"featuretype": "Categorical"}'
```

Expected Output:

```bash
{"featuretype":"Categorical","name":"col0"}
```