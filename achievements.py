ACHIEVEMENTS = {
    "first_word": {
        "name": "🌱 اولین کلمه",
        "description": "اولین کلمه‌ت رو ذخیره کردی!",
        "icon": "🌱",
        "condition": lambda stats: stats["total_words"] >= 1
    },
    "five_words": {
        "name": "📚 پنج کلمه‌ای",
        "description": "۵ کلمه ذخیره کردی!",
        "icon": "📚",
        "condition": lambda stats: stats["total_words"] >= 5
    },
    "ten_words": {
        "name": "🎯 ده کلمه‌ای",
        "description": "۱۰ کلمه یاد گرفتی!",
        "icon": "🎯",
        "condition": lambda stats: stats["total_words"] >= 10
    },
    "fifty_words": {
        "name": "🏆 پنجاه کلمه‌ای",
        "description": "۵۰ کلمه! عالیه!",
        "icon": "🏆",
        "condition": lambda stats: stats["total_words"] >= 50
    },
    "hundred_words": {
        "name": "👑 صد کلمه‌ای",
        "description": "۱۰۰ کلمه! استاد شدی!",
        "icon": "👑",
        "condition": lambda stats: stats["total_words"] >= 100
    },
    "streak_3": {
        "name": "🔥 سه روز پشت سر هم",
        "description": "۳ روز متوالی فعال بودی!",
        "icon": "🔥",
        "condition": lambda stats: stats["streak_days"] >= 3
    },
    "streak_7": {
        "name": "⚡ یه هفته کامل",
        "description": "۷ روز متوالی!",
        "icon": "⚡",
        "condition": lambda stats: stats["streak_days"] >= 7
    },
    "streak_30": {
        "name": "💎 یه ماه کامل",
        "description": "۳۰ روز متوالی! بی‌نظیری!",
        "icon": "💎",
        "condition": lambda stats: stats["streak_days"] >= 30
    },
    "quiz_master": {
        "name": "🎓 استاد کوئیز",
        "description": "۱۰ کوئیز رو با موفقیت جواب دادی!",
        "icon": "🎓",
        "condition": lambda stats: stats["correct_answers"] >= 10
    },
    "perfect_quiz": {
        "name": "⭐️ کوئیز کامل",
        "description": "۵ کوئیز پشت سر هم درست جواب دادی!",
        "icon": "⭐️",
        "condition": lambda stats: stats["correct_answers"] >= 5
    }
}


def check_new_achievements(user_stats: dict, current_achievements: list) -> list:
    """بررسی دستاوردهای جدید"""
    new_achievements = []
    for ach_id, ach_data in ACHIEVEMENTS.items():
        if ach_id not in current_achievements and ach_data["condition"](user_stats):
            new_achievements.append(ach_id)
    return new_achievements


def get_achievement_info(ach_id: str) -> dict:
    """دریافت اطلاعات یک دستاورد"""
    return ACHIEVEMENTS.get(ach_id, {})