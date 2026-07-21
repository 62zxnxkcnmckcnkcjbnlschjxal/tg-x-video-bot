FROM python:3.11-slim
# 安装yt-dlp必须的ffmpeg视频工具
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
# 复制仓库全部代码
COPY . .
# 安装python依赖
RUN pip install --no-cache-dir -r requirements.txt
# 启动机器人
CMD ["python", "bot.py"]
