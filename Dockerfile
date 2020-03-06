FROM python:3.8-alpine3.11

RUN apk add --no-cache libstdc++ g++ git

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY ./datasets /app/datasets
COPY ./setup.py /app/setup.py

RUN pip install /app/

COPY ./samples /samples

WORKDIR /app/

EXPOSE 8080

ENTRYPOINT ["python", "-m", "datasets.api"]
CMD ["--samples-config", "/samples/config.json"]
