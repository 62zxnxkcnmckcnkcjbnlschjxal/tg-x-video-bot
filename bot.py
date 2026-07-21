import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
import yt_dlp

# 读取环境变量
TOKEN = os.getenv("BOT_TOKEN")
# 代理配置，解决Railway无法访问TG接口（无代理可留空）
PROXY_URL = os.getenv("HTTPS_PROXY", "")
# 统一临时缓存目录
TEMP_DIR = "./temp_cache"
os.makedirs(TEMP_DIR, exist_ok=True)

async def handle_message(update: Update, context: CallbackContext):
    if not update.message or not update.message.text:
        return
    url = update.message.text.strip()
    if 'x.com' not in url and 'twitter.com' not in url:
        await update.message.reply_text("请发送 X/Twitter 视频链接！")
        return

    msg = await update.message.reply_text("🔄 正在下载视频，请稍等...")

    try:
        # 限定临时目录存放视频，避免根目录混乱
        ydl_opts = {
            'outtmpl': os.path.join(TEMP_DIR, '%(id)s.%(ext)s'),
            'format': 'best[height<=720][ext=mp4]',
            'quiet': True,
            'no_warnings': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await msg.edit_text("📤 正在发送视频...")
        # 上传视频
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption="✅ X视频下载完成")
        # 立刻删除缓存文件释放空间
        os.remove(filename)

    except Exception as e:
        err_msg = str(e)[:120]
        await msg.edit_text(f"❌ 下载失败: {err_msg}")

def main():
    # 校验Token是否存在
    if not TOKEN:
        raise RuntimeError("环境变量 BOT_TOKEN 未配置！")
    
    # 构建Bot实例，添加代理解决Railway网络封锁
    builder = Application.builder().token(TOKEN)
    if PROXY_URL:
        builder.proxy_url(PROXY_URL)
    app = builder.build()

    # 注册消息处理器
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Telegram X下载机器人启动成功")
    app.run_polling()

if __name__ == "__main__":
    main()
