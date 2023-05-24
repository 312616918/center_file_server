FROM --platform=linux/amd64 python:3.10.11-slim-buster

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt -i http://192.168.31.148:9160//root/public/+simple/ --trusted-host 192.168.31.148
RUN chmod +x /app/entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]