FROM python:3.10.9

WORKDIR /app
COPY requirements.txt requirements.txt
COPY main.py main.py

RUN pip install -r requirements.txt
CMD python main.py