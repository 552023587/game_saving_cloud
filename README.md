# Game Save Cloud

游戏云存档 — 支持多游戏的存档备份与恢复，服务端/客户端架构。

[English](README_EN.md)

## 架构

```
Server (FastAPI)  ←→  Client (PySide2 Qt5)
     端口 3000            GUI 桌面应用
```

- 服务端：REST API，SQLite 存储，文件系统存 zip 存档
- 客户端：游戏列表 + 详情面板，一键上传/下载存档

## 界面

![应用截图](app.png)

## 安装

```bash
pip install -r requirements.txt
```

## 运行

**服务端：**

```bash
# 直接运行
python server/main.py

# 或 uvicorn
uvicorn server.main:app --host 0.0.0.0 --port 3000
```

**客户端：**

```bash
python -m client.main
```

在客户端 "设置 → 服务器配置" 中填写服务端 IP。

## 配置

服务端通过环境变量配置（前缀 `GSC_`）：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `GSC_HOST` | `0.0.0.0` | 监听地址 |
| `GSC_PORT` | `3000` | 监听端口 |
| `GSC_DATABASE_URL` | `sqlite+aiosqlite:///./server/data/game_saves.db` | SQLite 路径 |
| `GSC_STORAGE_ROOT` | `./server/storage` | 存档文件存储目录 |
| `GSC_MAX_UPLOAD_SIZE_MB` | `500` | 最大上传大小 (MB) |
| `GSC_LOG_LEVEL` | `INFO` | 日志级别 |

## 打包

```bash
python build.py          # 服务端
python build.py client   # 客户端
```

输出在 `dist/` 目录。

## 部署服务端（Linux systemd）

```bash
sudo tee /etc/systemd/system/game-save-cloud.service << 'EOF'
[Unit]
Description=Game Save Cloud
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/allen/game_save_cloud/dist/game-save-server
ExecStart=/home/allen/game_save_cloud/dist/game-save-server/game-save-server
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now game-save-cloud
```

## API

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/health` | 健康检查 |
| GET | `/api/games` | 游戏列表 |
| POST | `/api/games` | 添加游戏 |
| GET | `/api/games/{id}` | 游戏详情 |
| PUT | `/api/games/{id}` | 更新游戏 |
| DELETE | `/api/games/{id}` | 删除游戏 |
| PUT | `/api/games/{id}/icon` | 上传图标 |
| GET | `/api/games/{id}/icon` | 下载图标 |
| POST | `/api/games/{id}/saves` | 上传单个存档 |
| GET | `/api/games/{id}/saves` | 查询游戏存档列表 |
| GET | `/api/saves/{id}/download` | 下载单个存档 |
| DELETE | `/api/saves/{id}` | 删除存档 |
| PUT | `/api/games/{id}/save` | 上传存档 zip |
| GET | `/api/games/{id}/save/download` | 下载存档 zip |
