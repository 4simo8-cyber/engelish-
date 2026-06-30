from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
import database

scheduler = AsyncIOScheduler()


async def send_daily_reminder(bot: Bot, user_id: str, words_to_review: list):
    """ارسال یادآور روزانه با کلمات مرور"""
    user = database.get_user(user_id)

    if not words_to_review:
        text = (
            "🌅 صبح بخیر! وقت یادگیریه!\n\n"
            "📚 امروز می‌تونی چند کلمه‌ی جدید یاد بگیری.\n"
            "فقط یه کلمه برام بفرست تا شروع کنیم! 🚀"
        )
    else:
        text = "🌅 یادآور روزانه‌ت!\n\n📚 امروز وقت مرور این کلماته:\n\n"
        for i, item in enumerate(words_to_review[:5], 1):
            text += f"{i}. {item['word']} — {item['sentence']}\n"
        text += "\n💪 مرور کن و بعد برو دنبال کلمات جدید!"

    try:
        await bot.send_message(chat_id=int(user_id), text=text, parse_mode="Markdown")
    except Exception as e:
        print(f"Error: {e}")


def setup_scheduler(bot: Bot):
    """راه‌اندازی scheduler"""
    scheduler.start()
    return scheduler


def schedule_user_reminder(user_id: str, time_str: str, bot: Bot, words: list):
    """زمان‌بندی یادآور برای کاربر"""
    hour, minute = map(int, time_str.split(":"))
    job_id = f"reminder_{user_id}"

    try:
        scheduler.remove_job(job_id)
    except:
        pass

    scheduler.add_job(
        send_daily_reminder,
        CronTrigger(hour=hour, minute=minute),
        args=[bot, user_id, words],
        id=job_id,
        replace_existing=True
    )