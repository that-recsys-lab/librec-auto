FROM python:3.8-slim

CMD apt-get update && apt-get install python3

COPY . /.

RUN pip3 install -r requirements.txt

RUN python3 setup.py install
CMD python3 -m librec_auto
