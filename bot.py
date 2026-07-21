import os
import traceback
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
import yt_dlp

# 读取Railway环境变量
TOKEN = os.getenv("BOT_TOKEN")
PROXY_URL = os.getenv("HTTPS_PROXY", "")
# 临时视频缓存文件夹
TEMP_DIR = "./temp_cache"
os.makedirs(TEMP_DIR, exist_ok=True)

async def handle_download(update: Update, context: CallbackContext):
    # 兼容私聊/群组消息
    msg_text = update.effective_message.text.strip()
    if not msg_text:
        return
    # 匹配X/Twitter链接
    if "x.com" not in msg_text and "twitter.com" not in msg_text:
        return
    wait_msg = await update.effective_message.reply_text("🔄 解析X视频中，请等待...")
    file_path = None
    try:
        ydl_config = {
            "outtmpl": os.path.join(TEMP_DIR, "%(id)s.%(ext)s"),
            "format": "best[height<=720][ext=mp4]",
            "quiet": True,
            "no_warnings": True,
            "socket_timeout": 30
        }
        with yt_dlp.YoutubeDL(ydl_config) as ydl:
            video_info = ydl.extract_info(msg_text, download=True)
            file_path = ydl.prepare_filename(video_info)
        await wait_msg.edit_text("📤 正在上传视频...")
        # 发送视频到群/私聊
        with open(file_path, "rb") as f:
            await update.effective_message.reply_video(video=f, caption="✅ X视频提取完成")
    except Exception as err:
        print(traceback.format_exc())
        await wait_msg.edit_text(f"❌ 下载失败：{str(err)[:120]}")
    finally:
        # 强制删除缓存，防止磁盘占满
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

def main():
    if not TOKEN:
        raise RuntimeError("未配置环境变量 BOT_TOKEN")
    # 构建Bot，支持代理解决Railway网络屏蔽TG
    app_builder = Application.builder().token(TOKEN)
    if PROXY_URL:
        app_builder.proxy_url(PROXY_URL)
    app = app_builder.build()
    # 监听所有文本消息（群聊/私聊全部生效）
    app.add_handler(MessageHandler(filters.TEXT, handle_download))
    print("✅ Bot启动成功，私聊/群组均可使用")
    app.run_polling()

if __name__ == "__main__":
    main()
