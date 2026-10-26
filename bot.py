import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from news.models import Category, News

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1004257392441
ADMIN_IDS = {5341856826}

async def forward_to_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("You're not authorized to post to this channel!")
        return

    msg = update.message
    parsed_news = parse_news_message(msg.caption or msg.text)
    await sync_to_async(save_to_db)(parsed_news)

    if msg.text:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=msg.text)

    elif msg.photo:
        file_id = msg.photo[-1].file_id
        await context.bot.send_photo(chat_id=CHANNEL_ID, photo=file_id, caption=msg.caption)

    elif msg.video:
        await context.bot.send_video(chat_id=CHANNEL_ID, video=msg.video.file_id, caption=msg.caption)

    elif msg.document:
        await context.bot.send_document(chat_id=CHANNEL_ID, document=msg.document.file_id, caption=msg.caption)

    elif msg.audio:
        await context.bot.send_audio(chat_id=CHANNEL_ID, audio=msg.audio.file_id, caption=msg.caption)

    else:
        await update.message.reply_text("Unsupported message type.")
        return

    await update.message.reply_text("Posted to channel.")



# WEBSITE PART
# parsing
def parse_news_message(text: str):
    lines = text.split('\n', 1)
    category = lines[0][1:].strip()
    rest = lines[1].strip()
    parts = rest.split('\n', 1)
    title = parts[0].strip()
    content = parts[1].strip()

    return {'category': category, 'title': title, 'content': content}


# creating news and adding categories
def save_to_db(news: dict):
    category, created = Category.objects.get_or_create(name=news["category"])
    News.objects.create(
        title=news['title'],
        content=news['content'],
        category=category
    )
    print('Saved to db my boi!')


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(
        filters.ChatType.PRIVATE & (filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.ALL | filters.AUDIO),
        forward_to_channel
    ))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()