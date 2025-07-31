## 启动
```bash
# 根目录下
uvicorn rest_api.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile ./.vscode/tools/cert/localhost.key --ssl-certfile ./.vscode/tools/cert/localhost.crt

```

### compose
```bash
cd # 根目录下

docker-compose -f ./rest_api/docker-compose.yml  --project-directory . up -d --build

# nas 启动
docker compose -f ./rest_api/.docker/nas-docker.yml --profile management --project-directory . up -d
```