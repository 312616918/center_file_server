FROM --platform=linux/amd64 python:3.10.11-slim-buster

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENTRYPOINT ["/app/entrypoint.sh"]