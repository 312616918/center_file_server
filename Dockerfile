FROM python:3.10.11-slim-buster

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENTRYPOINT ["entrypoint.sh"]