FROM python:3.9-slim

WORKDIR /usr/src/app

RUN apt-get clean && \
    apt-get update && \
    apt-get install -y --no-install-recommends wget unzip libnss3 && \
    pip install PyJWT pytest-playwright networkx[all] numpy && \
    playwright install-deps && playwright install

COPY . .

CMD ["python", "./vsm_visualizer_v2.py"]
