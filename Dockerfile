FROM python:3

ADD proxyfeeder.py /

RUN pip install --upgrade pip && \
    pip install pika requests

CMD [ "python", "./proxyfeeder.py"]
