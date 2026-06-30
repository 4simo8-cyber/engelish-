import openai
import json
import os

openai.api_key = os.getenv("OPENAI_API_KEY")


async def generate_sentence(word: str, level: str = "beginner") -> dict:
    level_info = {
        "beginner": "A1-A2 level, simple present tense, basic vocabulary, maximum 8 words",
        "intermediate": "B1-B2 level, mix of tenses, maximum 12 words",
        "advanced": "C1 level, complex structures, idioms, maximum 15 words"
    }

    prompt = f"""Create an English example sentence using the word "{word}".

Level: {level_info.get(level, level_info['beginner'])}

Reply in JSON format ONLY:
{{
    "sentence": "the English sentence",
    "translation": "Persian (Farsi) translation",
    "word_type": "part of speech",
    "pronunciation": "IPA phonetic transcription",
    "explanation": "brief explanation in Persian"
}}"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an English teacher for Persian speakers. Always reply with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip().rstrip("").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error: {e}")
        return {
            "sentence": f"I like the word {word}.",
            "translation": f"من کلمه {word} را دوست دارم.",
            "word_type": "word",
            "pronunciation": "/" + word + "/",
            "explanation": "یک جمله‌ی ساده."
        }


async def generate_quiz(word: str, sentence: str) -> dict:
    prompt = f"""Create a multiple choice quiz for the English word "{word}" used in: "{sentence}"

Create 4 options where ONLY ONE is correct.

Reply in JSON format ONLY:
{{
    "question": "question in Persian",
    "question_en": "question in English",
    "options": ["option 1", "option 2", "option 3", "option 4"],
    "correct_index": 0,
    "explanation": "why this is correct, in Persian"
}}"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an English teacher. Always reply with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("``"):
            content = content.split("")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip().rstrip("").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error: {e}")
        return {
            "question": f"معنی کلمه '{word}' چیست؟",
            "question_en": f"What does '{word}' mean?",
            "options": ["گزینه ۱", "گزینه ۲", "گزینه ۳", "گزینه ۴"],
            "correct_index": 0,
            "explanation": "خطا در ساخت کوئیز."
        }