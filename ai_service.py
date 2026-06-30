import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


async def generate_sentence(word: str, level: str = "beginner") -> dict:
    level_info = {
        "beginner": "A1-A2, very simple, present tense, max 8 words",
        "intermediate": "B1-B2, mix of tenses, max 12 words",
        "advanced": "C1, complex structures, idioms, max 15 words"
    }

    prompt = f"""Create an English example sentence for the word "{word}".
Level: {level_info.get(level, level_info['beginner'])}

Respond ONLY in valid JSON (no markdown, no explanation):
{{
    "sentence": "English sentence using the word",
    "translation": "Persian (Farsi) translation",
    "word_type": "part of speech (noun/verb/adj/adv)",
    "pronunciation": "IPA like /əˈpæl/",
    "explanation": "short explanation in Persian"
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful English teacher. Always respond with valid JSON only, no markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip().rstrip("`").strip()
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
    prompt = f"""Create a multiple choice quiz for "{word}" used in: "{sentence}"

Respond ONLY in valid JSON (no markdown):
{{
    "question": "question in Persian",
    "question_en": "question in English",
    "options": ["A) text", "B) text", "C) text", "D) text"],
    "correct_index": 0,
    "explanation": "why in Persian"
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful English teacher. Always respond with valid JSON only, no markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip().rstrip("`").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error: {e}")
        return {
            "question": f"معنی '{word}' چیست؟",
            "question_en": f"What does '{word}' mean?",
            "options": ["A) option 1", "B) option 2", "C) option 3", "D) option 4"],
            "correct_index": 0,
            "explanation": "خطا در ساخت کوئیز."
        }                {"role": "user", "content": prompt}
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
