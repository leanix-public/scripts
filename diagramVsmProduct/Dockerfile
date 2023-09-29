FROM python:3.9-slim

WORKDIR /usr/src/app

RUN pip install requests PyJWT networkx[all] numpy

COPY . .

CMD ["python", "./diagram_vsm_product.py"]
