FROM ubuntu:20.04
COPY ./ /work
RUN mkdir -p /work/results
WORKDIR /work/eval
RUN apt-get update && apt-get install -y python3 python3-pip python3-dev gcc g++ libffi-dev libssl-dev
RUN pip install cython
RUN pip install cryptography
RUN pip install gunicorn
RUN pip install -r /work/deploy/requirements.txt

EXPOSE 5000

ENTRYPOINT ["gunicorn", "--workers=4", "--log-level", "debug", "--bind=0.0.0.0:5000", "deploy:app"]