from data.db_manager import DBManager
import random
import json
from logic.gemini_api import call_gemini_json_response
from logic.performance_analyzer import analyze_test_performance
from logger import logger  # Logger'ı import et

def generate_mc_questions_json(konu: str, alt_konu: str, zorluk: str, soru_sayisi: int) -> str:
    logger.info(f"generate_mc_questions_json çağrıldı: konu={konu}, alt_konu={alt_konu}, zorluk={zorluk}, soru_sayisi={soru_sayisi}")
    prompt = f"""
Konu: "{konu}"
Alt konu: "{alt_konu}"
Zorluk düzeyi: {zorluk}
Soru sayısı: {soru_sayisi}

Yukarıdaki bilgilere göre çoktan seçmeli {soru_sayisi} adet soru üret.

Her soru için:
- Soru metni (açık ve doğru)
- 4 adet seçenek (karışık sırayla)
- Doğru cevap (tek bir seçenek)
- Kısa açıklama (neden doğru olduğu)

Lütfen yalnızca aşağıdaki JSON formatında çıktı ver.
"""

    system_instruction = "Yanıt sadece JSON formatında olsun. Her sorunun şıkları, cevabı ve açıklaması eksiksiz yer almalı."

    output_schema = {
        "type": "object",
        "required": ["sorular"],
        "properties": {
            "sorular": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["konu", "alt_konu", "zorluk", "soru", "secenekler", "dogru_cevap", "aciklama"],
                    "properties": {
                        "konu": {"type": "string"},
                        "alt_konu": {"type": "string"},
                        "zorluk": {"type": "string"},
                        "soru": {"type": "string"},
                        "secenekler": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 4,
                            "maxItems": 4
                        },
                        "dogru_cevap": {"type": "string"},
                        "aciklama": {"type": "string"},
                    }
                }
            }
        }
    }

    try:
        result = call_gemini_json_response(prompt, system_instruction, output_schema)
        logger.info("generate_mc_questions_json başarılı şekilde tamamlandı.")
        return result
    except Exception as e:
        logger.exception(f"generate_mc_questions_json sırasında hata: {e}")
        raise


def generate_question_for_topic(topic: str, difficulty: str = "medium", count: int = 5) -> list[dict]:
    logger.info(f"generate_question_for_topic çağrıldı: topic={topic}, difficulty={difficulty}, count={count}")

    prompt = f"""
Konu: {topic}
Zorluk: {difficulty}
Soru sayısı: {count}

Aşağıdaki kurallara göre {count} adet çoktan seçmeli soru oluştur:

1. Her soru açık ve net olmalı.
2. 4 farklı seçenek içermeli.
3. Yalnızca 1 doğru cevap olmalı.
4. Doğru cevap pozisyon olarak (A/B/C/D) belirtilmeli.
5. Kısa açıklama (çözüm) eklenmeli.
6. Şıklar birden fazla doğru içeremez.

Lütfen aşağıdaki JSON formatında yanıt ver:

{{
  "sorular": [
    {{
      "question": "Soru metni",
      "options": ["option1", "option2", "option3", "option4"],
      "correct_answer": "B",
      "explanation": "Kısa açıklama"
    }},
    ...
  ]
}}
    """

    system_instruction = "Bu bir test uygulamasıdır. Lütfen sadece geçerli JSON formatı döndür. Şıklar arasında sadece bir doğru olsun."

    schema = {
        "type": "object",
        "required": ["sorular"],
        "properties": {
            "sorular": {
                "type": "array",
                "minItems": count,
                "items": {
                    "type": "object",
                    "required": ["question", "options", "correct_answer", "explanation"],
                    "properties": {
                        "question": {"type": "string"},
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 4,
                            "maxItems": 4,
                            "uniqueItems": True
                        },
                        "correct_answer": {
                            "type": "string",
                            "enum": ["A", "B", "C", "D"]
                        },
                        "explanation": {"type": "string"}
                    }
                }
            }
        }
    }

    try:
        response = call_gemini_json_response(prompt, system_instruction, schema)
        if isinstance(response, str):
            response = json.loads(response)

        formatted_questions = []

        for item in response["sorular"]:
            options = item["options"]
            correct_letter = item["correct_answer"].upper()

            index_map = {"A": 0, "B": 1, "C": 2, "D": 3}
            correct_index = index_map.get(correct_letter, -1)
            if correct_index == -1:
                raise ValueError(f"Geçersiz doğru cevap harfi: {correct_letter}")

            correct_option_text = options[correct_index]

            shuffled_options = options[:]
            random.shuffle(shuffled_options)

            new_correct_index = shuffled_options.index(correct_option_text)
            new_correct_letter = ["A", "B", "C", "D"][new_correct_index]

            labeled_options = [f"{label}) {opt}" for label, opt in zip(["A", "B", "C", "D"], shuffled_options)]

            formatted_questions.append({
                "question": item["question"],
                "options": labeled_options,
                "correct_answer": new_correct_letter,
                "explanation": item["explanation"],
                "topic": topic
            })

        logger.info("generate_question_for_topic başarıyla tamamlandı.")
        return formatted_questions

    except Exception as e:
        logger.exception(f"generate_question_for_topic sırasında hata: {e}")
        raise


def generate_questions_from_analysis(analysis: list, total_questions: int) -> list:
    logger.info(f"generate_questions_from_analysis çağrıldı, toplam soru sayısı: {total_questions}")

    weighted_topics = [item["topic"] for item in analysis]
    weights = [item["weight"] for item in analysis]

    selected_topics = random.choices(weighted_topics, weights=weights, k=total_questions)

    topic_counts = {}
    for topic in selected_topics:
        topic_counts[topic] = topic_counts.get(topic, 0) + 1

    generated_questions = []

    for topic, count in topic_counts.items():
        difficulty = next((item["difficulty"] for item in analysis if item["topic"] == topic), "medium")

        try:
            question_batch = generate_question_for_topic(topic=topic, difficulty=difficulty, count=count)

            for q in question_batch:
                if not all(k in q for k in ["question", "options", "correct_answer", "explanation"]):
                    raise ValueError("Eksik alan var")

                options = q["options"]
                correct = q["correct_answer"].strip().upper()

                if correct not in ["A", "B", "C", "D"]:
                    raise ValueError("Geçersiz doğru cevap formatı")

                generated_questions.append({
                    "question": q["question"],
                    "options": options,
                    "correct_answer": correct,
                    "explanation": q["explanation"],
                    "topic": topic
                })

        except Exception as e:
            logger.error(f"Soru üretilemedi ({topic}) → {e}")
            continue

    logger.info(f"generate_questions_from_analysis tamamlandı, toplam üretilen soru: {len(generated_questions)}")
    return generated_questions
