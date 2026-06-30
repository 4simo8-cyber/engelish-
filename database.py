import json
import os
from datetime import datetime, timedelta

DB_FILE = "user_database.json"


def load_db():
    """بارگذاری دیتابیس از فایل"""
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_db(data):
    """ذخیره دیتابیس در فایل"""
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_user(user_id: str)-> dict:
    """دریافت اطلاعات کاربر یا ساخت کاربر جدید"""
    db = load_db()
    if user_id not in db:
        db[user_id] = {
            "level": "beginner",
            "saved_words": [],
            "stats": {
                "total_words": 0,
                "today_words": 0,
                "last_active_date": "",
                "streak_days": 0,
                "total_sentences": 0,
                "quizzes_taken": 0,
                "correct_answers": 0
            },
            "flashcards": {},
            "achievements": [],
            "daily_reminder": True,
            "reminder_time": "09:00"
        }
        save_db(db)
    return db[user_id]


def save_user(user_id: str, user_data: dict):
    """ذخیره اطلاعات کاربر"""
    db = load_db()
    db[user_id] = user_data
    save_db(db)


def update_stats(user_id: str, **kwargs):
    """به‌روزرسانی آمار کاربر و محاسبه streak"""
    db = load_db()
    user = get_user(user_id)
    today = datetime.now().strftime("%Y-%m-%d")

    # به‌روزرسانی فیلدهای آمار
    for key, value in kwargs.items():
        if key in user["stats"]:
            user["stats"][key] = value

    # بررسی و به‌روزرسانی streak روزانه
    if user["stats"]["last_active_date"] != today:
        if user["stats"]["last_active_date"]:
            last_date = datetime.strptime(user["stats"]["last_active_date"], "%Y-%m-%d")
            if datetime.now() - last_date == timedelta(days=1):
                user["stats"]["streak_days"] += 1
            else:
                user["stats"]["streak_days"] = 1
        else:
            user["stats"]["streak_days"] = 1
        user["stats"]["last_active_date"] = today
        user["stats"]["today_words"] = 0

    save_user(user_id, user)