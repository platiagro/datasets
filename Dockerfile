FROM python:3.8-buster

LABEL maintainer="fabiol@cpqd.com.br"

# Stamps the commit SHA into the labels and ENV vars
ARG BRANCH="master"
ARG COMMIT=""
LABEL branch=${BRANCH}
LABEL commit=${COMMIT}
ENV COMMIT=${COMMIT}
ENV BRANCH=${BRANCH}

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./datasets /app/datasets
COPY ./setup.py /app/setup.py

RUN pip install /app/

COPY ./samples /samples

WORKDIR /app/

EXPOSE 8080

ENTRYPOINT ["uvicorn", "datasets.api:app"]
CMD ["--host", "0.0.0.0", "--port", "8080", "--workers", "4"]
