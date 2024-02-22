FROM ubuntu:20.04
COPY ./ /work
RUN mkdir -p /work/results
RUN mkdir -p /work/certs
WORKDIR /work/eval
RUN apt-get update && apt-get install -y python3 python3-pip python3-dev gcc g++ libffi-dev libssl-dev
RUN pip install cython
RUN pip install cryptography
RUN pip install gunicorn
RUN pip install -r /work/deploy/requirements.txt

EXPOSE 5000

ENTRYPOINT ["gunicorn", "--workers=4", "--log-level", "debug", "--bind=0.0.0.0:5000", "deploy:app"]


# RUN openssl req -x509 -newkey rsa:4096 -nodes -out /work/certs/cert.pem -keyout /work/certs/key.pem -days 365 -batch

# EXPOSE 5000

# ENTRYPOINT ["gunicorn", "--certfile=/work/certs/cert.pem", "--keyfile=/work/certs/key.pem", "--workers=4", "--log-level", "debug", "--bind=0.0.0.0:5000", "deploy:app"]