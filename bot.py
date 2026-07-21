import os
import traceback
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# 环境变量读取
BOT_TOKEN = os.getenv("BOT_TOKEN")
PROXY = os.getenv("HTTPS_PROXY", "")
TEMP_DIR = "./temp_cache"
os.makedirs(TEMP_DIR, exist_ok=True)

import yt_dlp

async def download_handler(update: Update, context):
    text = update.effective_message.text.strip()
    if not ("x.com" in text or "twitter.com" in text):
        return

    wait_msg = await update.effective_message.reply_text("🔄 正在解析X视频...")
    video_path = None
    try:
        ydl_opts = {
            "outtmpl": os.path.join(TEMP_DIR, "%(id)s.mp4"),
            "format": "best[height<=720][ext=mp4]",
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 30
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(text, download=True)
            video_path = ydl.prepare_filename(info)

        await wait_msg.edit_text("📤 上传视频中...")
        with open(video_path, "rb") as f:
            await update.effective_message.reply_video(video=f, caption="✅ X视频下载完成")

    except Exception as e:
        print(traceback.format_exc())
        await wait_msg.edit_text(f"❌ 失败：{str(e)[:100]}")
    finally:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)

def main():
    if not BOT_TOKEN:
        raise RuntimeError("未配置环境变量 BOT_TOKEN")
    
    # 标准20.x新版构建方式，无Updater兼容bug
    app = ApplicationBuilder().token(BOT_TOKEN)
    if PROXY:
        app.proxy_url(PROXY)
    app = app.build()

    # 监听全部文本消息，私聊/群组通用
    app.add_handler(MessageHandler(filters.TEXT, download_handler))
    print("✅ Bot启动成功，支持私聊、群组")
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
