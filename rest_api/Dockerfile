FROM python:3.10-slim-bookworm

# RUN pip install uv

WORKDIR /app

COPY ./rest_api/ ./rest_api/

RUN pip install --no-cache-dir -r rest_api/requirements.txt -i https://mirrors.aliyun.com/pypi/simple

EXPOSE 8503

CMD [ "uvicorn", "rest_api.main:app", "--host", "0.0.0.0", "--port", "8503"]
