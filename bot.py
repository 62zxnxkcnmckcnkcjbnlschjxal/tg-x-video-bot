import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
import yt_dlp

TOKEN = os.getenv("BOT_TOKEN")

async def handle_message(update: Update, context: CallbackContext):
    if not update.message or not update.message.text:
        return
    url = update.message.text.strip()
    if 'x.com' not in url and 'twitter.com' not in url:
        await update.message.reply_text("请发送 X/Twitter 视频链接！")
        return

    msg = await update.message.reply_text("🔄 正在下载视频，请稍等...")

    try:
        ydl_opts = {'outtmpl': '%(title)s.%(ext)s', 'format': 'best[height<=720]', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await msg.edit_text("📤 正在发送...")
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption="✅ 下载完成！")
        os.remove(filename)
    except Exception as e:
        await msg.edit_text(f"❌ 失败: {str(e)[:100]}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
