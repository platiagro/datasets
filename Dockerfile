FROM python:3.8-alpine3.11

RUN apk add --no-cache libstdc++ g++

COPY ./datasets /app/datasets
COPY ./setup.py /app/setup.py

RUN pip install /app/

WORKDIR /app/

EXPOSE 8080

CMD ["python", "-m", "datasets.api"]
