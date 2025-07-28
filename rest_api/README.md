## 启动
```bash
# 根目录下
uvicorn rest_api.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile ./.vscode/tools/cert/localhost.key --ssl-certfile ./.vscode/tools/cert/localhost.crt

```