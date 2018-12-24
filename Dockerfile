FROM python:3.6

RUN mkdir /src
COPY . /src

WORKDIR /src

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
