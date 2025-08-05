import json
from collections import defaultdict
from logger import logger  # logger.py'deki logger'ı import et

def analyze_topics_with_weights(test_records, min_questions=5):
    """
    Kullanıcının geçmiş test verilerine göre:
    - Konu bazlı başarı oranı hesaplar
    - Başarı oranına göre ağırlıklandırılmış zorluk önerisi verir
    - Daha zayıf olunan konulara daha yüksek ağırlık atar

    Dönüş:
    [
        {"topic": "Konu A", "success_rate": 40.0, "difficulty": "easy", "weight": 0.35},
        ...
    ]
    """
    logger.info(f"analyze_topics_with_weights fonksiyonu çağrıldı, kayıt sayısı: {len(test_records)}")
    
    topic_stats = defaultdict(lambda: {"correct": 0, "wrong": 0})

    try:
        for _, _, test_json, correct, wrong, _ in test_records:
            try:
                test_data = json.loads(test_json)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e} - Data: {test_json}")
                continue  # Bozuk json geçilsin

            for q in test_data:
                topic = q.get("topic", "GENEL")
                if q["user_answer"] == q["correct_answer"]:
                    topic_stats[topic]["correct"] += 1
                else:
                    topic_stats[topic]["wrong"] += 1

        analysis = []
        total_inverse_success = 0

        for topic, stats in topic_stats.items():
            total = stats["correct"] + stats["wrong"]
            if total < min_questions:
                logger.debug(f"'{topic}' konusu yetersiz veri ({total} soru), atlandı.")
                continue

            success_rate = stats["correct"] / total
            inverse_score = 1 - success_rate
            total_inverse_success += inverse_score

            if success_rate >= 0.8:
                level = "hard"
            elif success_rate >= 0.5:
                level = "medium"
            else:
                level = "easy"

            analysis.append({
                "topic": topic,
                "success_rate": round(success_rate * 100, 2),
                "difficulty": level,
                "inverse_score": inverse_score
            })

        for item in analysis:
            item["weight"] = round(item["inverse_score"] / total_inverse_success, 3) if total_inverse_success > 0 else 0
            del item["inverse_score"]

        analysis.sort(key=lambda x: x["success_rate"])

        logger.info(f"analyze_topics_with_weights fonksiyonu başarıyla tamamlandı, {len(analysis)} konu analiz edildi.")
        return analysis
    
    except Exception as e:
        logger.exception(f"analyze_topics_with_weights fonksiyonunda beklenmeyen hata: {e}")
        raise  # İstersen burada hatayı yukarı fırlatabilirsin
