FROM ubuntu:20.04
RUN mkdir /work
COPY ../eval /work
WORKDIR /work
RUN apt-get update && apt-get install -y python3 python3-pip python3-dev gcc g++ libffi-dev libssl-dev
RUN pip install cython
RUN pip install cryptography
RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "deploy:app"]