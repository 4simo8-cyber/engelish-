import logging
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from dotenv import load_dotenv

import database
import ai_service
import achievements as ach
import scheduler

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# ==================== دستورات اصلی ====================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    database.get_user(user_id)

    keyboard = [
        [InlineKeyboardButton("📚 سطح مبتدی", callback_data="level_beginner")],
        [InlineKeyboardButton("📖 سطح متوسط", callback_data="level_intermediate")],
        [InlineKeyboardButton("🎓 سطح پیشرفته", callback_data="level_advanced")],
        [InlineKeyboardButton("📊 آمار من", callback_data="stats")],
        [InlineKeyboardButton("🎯 فلش‌کارت", callback_data="flashcards")],
        [InlineKeyboardButton("🏆 دستاوردها", callback_data="achievements")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "👋 سلام! به ربات یادگیری زبان خوش اومدی! ✨\n\n"
        "📝 فقط یه کلمه‌ی انگلیسی بفرست تا:\n"
        "✅ یه جمله‌ی ساده بسازم\n"
        "✅ ترجمه‌ی فارسی بدم\n"
        "✅ تلفظ فونتیک نشون بدم\n"
        "✅ توضیح بدم\n\n"
        "مثال: apple یا run یا happy\n\n"
        "ابتدا یکی از گزینه‌ها رو انتخاب کن:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 راهنمای ربات:\n\n"
        "🔹 یه کلمه بفرست → جمله + ترجمه + تلفظ\n"
        "🔹 💾 ذخیره → کلمه به لیستت اضافه می‌شه\n"
        "🔹 🎯 کوئیز → ازت تست می‌گیره\n"
        "🔹 🎯 فلش‌کارت → مرور کلمات ذخیره‌شده\n"
        "🔹 📊 آمار → پیشرفتت رو ببین\n"
        "🔹 🏆 دستاوردها → جایزه بگیر\n\n"
        "دستورات:\n"
        "/start - شروع\n"
        "/level - تغییر سطح\n"
        "/stats - آمار\n"
        "/mylist - کلمات ذخیره‌شده\n"
        "/flashcards - فلش‌کارت\n"
        "/quiz - کوئیز تصادفی\n"
        "/achievements - دستاوردها\n"
        "/reminder - تنظیم یادآور روزانه\n"
        "/help - راهنما",
        parse_mode="Markdown"
    )


async def level_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 مبتدی (A1-A2)", callback_data="level_beginner")],
        [InlineKeyboardButton("📖 متوسط (B1-B2)", callback_data="level_intermediate")],
        [InlineKeyboardButton("🎓 پیشرفته (C1)", callback_data="level_advanced")]
    ]
    await update.message.reply_text("سطح خودت رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user = database.get_user(user_id)
    stats = user["stats"]

    level_names = {"beginner": "📚 مبتدی", "intermediate": "📖 متوسط", "advanced": "🎓 پیشرفته"}

    text = (
        "📊 آمار شما:\n\n"
        f"📚 کل کلمات ذخیره‌شده: {stats['total_words']}\n"
        f"📅 کلمات امروز: {stats['today_words']}\n"
        f"🔥 روزهای متوالی: {stats['streak_days']}\n"
        f"📝 کل جملات ساخته‌شده: {stats['total_sentences']}\n"
        f"🎓 کوئیزها: {stats['quizzes_taken']} ({stats['correct_answers']} درست)\n"
        f"🎯 سطح فعلی: {level_names.get(user['level'])}\n"
        f"🏆 دستاوردها: {len(user['achievements'])}/{len(ach.ACHIEVEMENTS)}\n"
    )

    await update.message.reply_text(text, parse_mode="Markdown")


async def mylist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user = database.get_user(user_id)
    saved = user["saved_words"]

    if not saved:
        await update.message.reply_text("📭 هنوز کلمه‌ای ذخیره نکردی!\n\nیه کلمه بفرست و 💾 ذخیره رو بزن.")
        return

    text = "📚 کلمات ذخیره‌شده‌ت:\n\n"
    for i, item in enumerate(saved[-15:], 1):
        text += f"{i}. {item['word']} — {item['sentence']}\n"

    keyboard = [
        [InlineKeyboardButton("🎯 شروع فلش‌کارت", callback_data="flashcards")],
        [InlineKeyboardButton("🗑 پاک کردن", callback_data="clear_confirm")]
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user = database.get_user(user_id)
    user["saved_words"] = []
    database.save_user(user_id, user)
    await update.message.reply_text("✅ لیست کلماتت پاک شد!")


async def achievements_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user = database.get_user(user_id)

    text = "🏆 دستاوردها:\n\n"

    earned = len(user["achievements"])
    total = len(ach.ACHIEVEMENTS)
    text += f"📊 پیشرفت: {earned}/{total}\n\n"

    for ach_id, ach_data in ach.ACHIEVEMENTS.items():
        if ach_id in user["achievements"]:
            text += f"{ach_data['icon']} {ach_data['name']} ✅\n_{ach_data['description']}_\n\n"
        else:
            text += f"🔒 _{ach_data['name']}_\n"

    await update.message.reply_text(text, parse_mode="Markdown")


async def reminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⏰ ۸ صبح", callback_data="reminder_08:00")],
        [InlineKeyboardButton("⏰ ۹ صبح", callback_data="reminder_09:00")],
        [InlineKeyboardButton("⏰ ۱۰ صبح", callback_data="reminder_10:00")],
        [InlineKeyboardButton("⏰ ۸ شب", callback_data="reminder_20:00")],
        [InlineKeyboardButton("⏰ ۹ شب", callback_data="reminder_21:00")],
        [InlineKeyboardButton("❌ غیرفعال", callback_data="reminder_off")]
    ]
    await update.message.reply_text(
        "🔔 ساعت یادآور روزانه‌ت رو انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==================== دریافت کلمه ====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip().lower()
    word = ''.join(c for c in text if c.isalpha() or c in "'-")

    if not word or len(word) > 30:
        await update.message.reply_text("⚠️ لطفاً فقط یه کلمه‌ی انگلیسی بفرست (حداکثر ۳۰ حرف).")
        return

    user = database.get_user(user_id)
    level = user["level"]

    wait_msg = await update.message.reply_text(f"⏳ در حال ساخت جمله با «{word}»...")

    result = await ai_service.generate_sentence(word, level)

    context.user_data["current_sentence"] = result
    context.user_data["current_word"] = word

    database.update_stats(user_id, total_sentences=user["stats"]["total_sentences"] + 1)

    keyboard = [
        [InlineKeyboardButton("🔄 جمله‌ی جدید", callback_data=f"new_{word}"),
         InlineKeyboardButton("🎯 کوئیز", callback_data=f"quiz_{word}")],
        [InlineKeyboardButton("💾 ذخیره", callback_data=f"save_{word}"),
         InlineKeyboardButton("🔊 تلفظ", callback_data=f"pronounce_{word}")],
        [InlineKeyboardButton("📚 کلمات من", callback_data="mylist")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    response = (
        f"📝 نوع: {result.get('word_type', 'word')}\n"
        f"🔊 تلفظ: {result.get('pronunciation', 'N/A')}\n\n"
        f"🇬🇧 جمله:\n_{result['sentence']}_\n\n"
        f"🇮🇷 ترجمه:\n_{result.get('translation', '')}_"
    )

    if result.get("explanation"):
        response += f"\n\n💡 {result['explanation']}"

    await wait_msg.edit_text(response, reply_markup=reply_markup, parse_mode="Markdown")

    # ==================== مدیریت دکمه‌ها ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = query.data

    # تغییر سطح
    if data.startswith("level_"):
        level = data.replace("level_", "")
        user = database.get_user(user_id)
        user["level"] = level
        database.save_user(user_id, user)
        names = {"beginner": "📚 مبتدی", "intermediate": "📖 متوسط", "advanced": "🎓 پیشرفته"}
        await query.edit_message_text(f"✅ سطح به {names.get(level)} تغییر کرد!\n\nحالا یه کلمه بفرست:")
        return

    # جمله‌ی جدید
    if data.startswith("new_"):
        word = data.replace("new_", "")
        await query.edit_message_text(f"⏳ ساخت جمله‌ی جدید...")
        user = database.get_user(user_id)
        result = await ai_service.generate_sentence(word, user["level"])
        context.user_data["current_sentence"] = result
        context.user_data["current_word"] = word

        keyboard = [
            [InlineKeyboardButton("🔄 جمله‌ی جدید", callback_data=f"new_{word}"),
             InlineKeyboardButton("🎯 کوئیز", callback_data=f"quiz_{word}")],
            [InlineKeyboardButton("💾 ذخیره", callback_data=f"save_{word}"),
             InlineKeyboardButton("🔊 تلفظ", callback_data=f"pronounce_{word}")],
            [InlineKeyboardButton("📚 کلمات من", callback_data="mylist")]
        ]
        response = (
            f"📝 نوع: {result.get('word_type', 'word')}\n"
            f"🔊 تلفظ: {result.get('pronunciation', 'N/A')}\n\n"
            f"🇬🇧 جمله:\n_{result['sentence']}_\n\n"
            f"🇮🇷 ترجمه:\n_{result.get('translation', '')}_"
        )
        await query.edit_message_text(response, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # ذخیره کلمه
    if data.startswith("save_"):
        word = data.replace("save_", "")
        current = context.user_data.get("current_sentence", {})
        if not current:
            await query.answer("❌ خطا!", show_alert=True)
            return
        user = database.get_user(user_id)
        saved = user["saved_words"]
        if not any(item["word"] == word for item in saved):
            now = datetime.now().isoformat()
            saved.append({
                "word": word,
                "sentence": current.get("sentence", ""),
                "translation": current.get("translation", ""),
                "pronunciation": current.get("pronunciation", ""),
                "explanation": current.get("explanation", ""),
                "added_at": now,
                "next_review": now,
                "interval": 1,
                "review_count": 0
            })
            user["saved_words"] = saved[-200:]
            user["stats"]["total_words"] = len(saved)
            user["stats"]["today_words"] = user["stats"].get("today_words", 0) + 1
            new_ach = ach.check_new_achievements(user["stats"], user["achievements"])
            if new_ach:
                user["achievements"].extend(new_ach)
            database.save_user(user_id, user)
            if new_ach:
                ach_text = "\n\n🏆 دستاورد جدید!\n"
                for a_id in new_ach:
                    info = ach.get_achievement_info(a_id)
                    ach_text += f"{info['icon']} {info['name']}\n"
                await query.answer(f"✅ ذخیره شد!{ach_text}", show_alert=True)
            else:
                await query.answer(f"✅ «{word}» ذخیره شد!", show_alert=False)
        else:
            await query.answer("⚠️ قبلاً ذخیره شده!", show_alert=False)
        return

    # کوئیز
    if data.startswith("quiz_"):
        word = data.replace("quiz_", "")
        current = context.user_data.get("current_sentence", {})

        sentence = current.get("sentence", "")
        await query.edit_message_text("🎯 در حال ساخت کوئیز...")
        quiz = await ai_service.generate_quiz(word, sentence)
        context.user_data["current_quiz"] = quiz
        keyboard = []
        for i, opt in enumerate(quiz["options"]):
            keyboard.append([InlineKeyboardButton(f"{chr(1553+i)} {opt}", callback_data=f"answer_{i}")])
        text = (
            f"🎯 کوئیز:\n\n"
            f"❓ {quiz.get('question_en', quiz.get('question', ''))}\n\n"
            f"_{quiz.get('question', '')}_\n\n"
            "گزینه‌ی درست رو انتخاب کن:"
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # جواب کوئیز
    if data.startswith("answer_"):
        idx = int(data.replace("answer_", ""))
        quiz = context.user_data.get("current_quiz", {})
        if not quiz:
            await query.answer("❌ خطا!", show_alert=True)
            return
        is_correct = idx == quiz.get("correct_index", -1)
        user = database.get_user(user_id)
        user["stats"]["quizzes_taken"] = user["stats"].get("quizzes_taken", 0) + 1
        if is_correct:
            user["stats"]["correct_answers"] = user["stats"].get("correct_answers", 0) + 1
        database.save_user(user_id, user)
        if is_correct:
            text = f"✅ آفرین! درست جواب دادی!\n\n💡 {quiz.get('explanation', '')}"
        else:
            correct = quiz["options"][quiz["correct_index"]]
            text = f"❌ اشتباه بود!\n\n✅ جواب درست: {correct}\n\n💡 {quiz.get('explanation', '')}"
        keyboard = [
            [InlineKeyboardButton("🔄 کوئیز جدید", callback_data=f"quiz_{context.user_data.get('current_word', '')}")],
            [InlineKeyboardButton("📚 کلمات من", callback_data="mylist")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # فلش‌کارت
    if data == "flashcards":
        user = database.get_user(user_id)
        if not user["saved_words"]:
            await query.edit_message_text("📭 هنوز کلمه‌ای ذخیره نکردی!")
            return
        cards = sorted(user["saved_words"], key=lambda x: x.get("review_count", 0))
        card = cards[0]
        context.user_data["current_card"] = card
        text = (
            f"🎯 فلش‌کارت ({len(user['saved_words'])} کلمه)\n\n"
            f"🇬🇧 {card['word']}\n"
            f"🔊 {card.get('pronunciation', '')}\n\n"
            "❓ معنی این کلمه چیست؟"
        )
        keyboard = [[InlineKeyboardButton("👀 دیدن جواب", callback_data="card_answer")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # نمایش جواب فلش‌کارت
    if data == "card_answer":
        card = context.user_data.get("current_card", {})
        text = (
            f"🇬🇧 {card['word']}\n"
            f"🔊 {card.get('pronunciation', '')}\n\n"
            f"🇮🇷 {card.get('translation', '')}\n\n"
            f"💡 {card.get('explanation', '')}\n\n"
            f"📝 _{card.get('sentence', '')}_"
        )
        keyboard = [
            [InlineKeyboardButton("😞 سخت بود", callback_data="card_hard"),
             InlineKeyboardButton("🙂 خوب بود", callback_data="card_good"),
             InlineKeyboardButton("😊 راحت بود", callback_data="card_easy")],
            [InlineKeyboardButton("⏭ بعدی", callback_data="flashcards")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # ارزیابی فلش‌کارت
    if data.startswith("card_"):
        difficulty = data.replace("card_", "")
        card = context.user_data.get("current_card", {})

        sentence = current.get("sentence", "")
        await query.edit_message_text("🎯 در حال ساخت کوئیز...")
        quiz = await ai_service.generate_quiz(word, sentence)
        context.user_data["current_quiz"] = quiz
        keyboard = []
        for i, opt in enumerate(quiz["options"]):
            keyboard.append([InlineKeyboardButton(f"{chr(1553+i)} {opt}", callback_data=f"answer_{i}")])
        text = (
            f"🎯 کوئیز:\n\n"
            f"❓ {quiz.get('question_en', quiz.get('question', ''))}\n\n"
            f"_{quiz.get('question', '')}_\n\n"
            "گزینه‌ی درست رو انتخاب کن:"
        )
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # جواب کوئیز
    if data.startswith("answer_"):
        idx = int(data.replace("answer_", ""))
        quiz = context.user_data.get("current_quiz", {})
        if not quiz:
            await query.answer("❌ خطا!", show_alert=True)
            return
        is_correct = idx == quiz.get("correct_index", -1)
        user = database.get_user(user_id)
        user["stats"]["quizzes_taken"] = user["stats"].get("quizzes_taken", 0) + 1
        if is_correct:
            user["stats"]["correct_answers"] = user["stats"].get("correct_answers", 0) + 1
        database.save_user(user_id, user)
        if is_correct:
            text = f"✅ آفرین! درست جواب دادی!\n\n💡 {quiz.get('explanation', '')}"
        else:
            correct = quiz["options"][quiz["correct_index"]]
            text = f"❌ اشتباه بود!\n\n✅ جواب درست: {correct}\n\n💡 {quiz.get('explanation', '')}"
        keyboard = [
            [InlineKeyboardButton("🔄 کوئیز جدید", callback_data=f"quiz_{context.user_data.get('current_word', '')}")],
            [InlineKeyboardButton("📚 کلمات من", callback_data="mylist")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # فلش‌کارت
    if data == "flashcards":
        user = database.get_user(user_id)
        if not user["saved_words"]:
            await query.edit_message_text("📭 هنوز کلمه‌ای ذخیره نکردی!")
            return
        cards = sorted(user["saved_words"], key=lambda x: x.get("review_count", 0))
        card = cards[0]
        context.user_data["current_card"] = card
        text = (
            f"🎯 فلش‌کارت ({len(user['saved_words'])} کلمه)\n\n"
            f"🇬🇧 {card['word']}\n"
            f"🔊 {card.get('pronunciation', '')}\n\n"
            "❓ معنی این کلمه چیست؟"
        )
        keyboard = [[InlineKeyboardButton("👀 دیدن جواب", callback_data="card_answer")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # نمایش جواب فلش‌کارت
    if data == "card_answer":
        card = context.user_data.get("current_card", {})
        text = (
            f"🇬🇧 {card['word']}\n"
            f"🔊 {card.get('pronunciation', '')}\n\n"
            f"🇮🇷 {card.get('translation', '')}\n\n"
            f"💡 {card.get('explanation', '')}\n\n"
            f"📝 _{card.get('sentence', '')}_"
        )
        keyboard = [
            [InlineKeyboardButton("😞 سخت بود", callback_data="card_hard"),
             InlineKeyboardButton("🙂 خوب بود", callback_data="card_good"),
             InlineKeyboardButton("😊 راحت بود", callback_data="card_easy")],
            [InlineKeyboardButton("⏭ بعدی", callback_data="flashcards")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # ارزیابی فلش‌کارت
    if data.startswith("card_"):
        difficulty = data.replace("card_", "")
        card = context.user_data.get("current_card", {})

        if card:
            intervals = {"hard": 1, "good": 3, "easy": 7}
            card["interval"] = intervals.get(difficulty, 3)
            card["review_count"] = card.get("review_count", 0) + 1
            card["next_review"] = datetime.now().isoformat()
            user = database.get_user(user_id)
            for i, item in enumerate(user["saved_words"]):
                if item["word"] == card["word"]:
                    user["saved_words"][i] = card
                    break
            database.save_user(user_id, user)
        await query.answer("✅ ثبت شد!")
        return await button_handler(update, context)

    # تلفظ
    if data.startswith("pronounce_"):
        word = data.replace("pronounce_", "")
        current = context.user_data.get("current_sentence", {})
        pron = current.get("pronunciation", "/" + word + "/")
        await query.answer(f"🔊 تلفظ: {pron}", show_alert=True)
        return

    # یادآور
    if data.startswith("reminder_"):
        value = data.replace("reminder_", "")
        user = database.get_user(user_id)
        if value == "off":
            user["daily_reminder"] = False
            database.save_user(user_id, user)
            await query.edit_message_text("❌ یادآور روزانه غیرفعال شد.")
        else:
            user["daily_reminder"] = True
            user["reminder_time"] = value
            database.save_user(user_id, user)
            bot = context.bot
            scheduler.schedule_user_reminder(user_id, value, bot, user["saved_words"])
            await query.edit_message_text(f"⏰ یادآور روزانه برای ساعت {value} تنظیم شد!", parse_mode="Markdown")
        return

    # آمار
    if data == "stats":
        user = database.get_user(user_id)
        stats = user["stats"]
        level_names = {"beginner": "📚 مبتدی", "intermediate": "📖 متوسط", "advanced": "🎓 پیشرفته"}
        text = (
            "📊 آمار شما:\n\n"
            f"📚 کل کلمات: {stats['total_words']}\n"
            f"📅 امروز: {stats['today_words']}\n"
            f"🔥 Streak: {stats['streak_days']} روز\n"
            f"📝 جملات ساخته‌شده: {stats['total_sentences']}\n"
            f"🎓 کوئیز: {stats['quizzes_taken']} ({stats['correct_answers']} درست)\n"
            f"🎯 سطح: {level_names.get(user['level'])}\n"
            f"🏆 دستاوردها: {len(user['achievements'])}/{len(ach.ACHIEVEMENTS)}"
        )
        await query.edit_message_text(text, parse_mode="Markdown")
        return

    # دستاوردها
    if data == "achievements":
        await achievements_command.callback(update, context)
        return

    # لیست کلمات
    if data == "mylist":
        await mylist_command.callback(update, context)
        return

    # تأیید پاک کردن
    if data == "clear_confirm":
        keyboard = [
            [InlineKeyboardButton("✅ بله، پاک کن", callback_data="clear_yes")],
            [InlineKeyboardButton("❌ انصراف", callback_data="mylist")]
        ]
        await query.edit_message_text("⚠️ مطمئنی می‌خوای همه کلماتت پاک شن؟", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # پاک کردن نهایی
    if data == "clear_yes":
        user = database.get_user(user_id)
        user["saved_words"] = []
        database.save_user(user_id, user)
        await query.edit_message_text("✅ همه کلماتت پاک شد!")
        return

    # راهنما
    if data == "help":
        await query.edit_message_text(
            "📚 راهنمای ربات:\n\n"
            "🔹 یه کلمه بفرست → جمله + ترجمه + تلفظ\n"
            "🔹 💾 ذخیره → کلمه به لیستت اضافه می‌شه\n"
            "🔹 🎯 کوئیز → ازت تست می‌گیره\n"
            "🔹 🎯 فلش‌کارت → مرور کلمات ذخیره‌شده\n"
            "🔹 📊 آمار → پیشرفتت رو ببین\n"
            "🔹 🏆 دستاوردها → جایزه بگیر",
            parse_mode="Markdown"
        )
        return


# ==================== اجرای ربات ====================
def main():
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("level", level_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("mylist", mylist_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("achievements", achievements_command))
    app.add_handler(CommandHandler("reminder", reminder_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))

    scheduler.setup_scheduler(app.bot)

    print("🤖 ربات در حال اجراست...")
    app.run_polling()


if __name__ == "main":
    main()