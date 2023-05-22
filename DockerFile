FROM python:3.10.11-slim-buster

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["entrypoint.sh"]