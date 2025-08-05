import json
from collections import defaultdict
from logger import logger

def analyze_test_performance(test_records):
    """
    Her konuya göre doğru/yanlış oranlarını analiz eder.
    """
    try:
        logger.info(f"analyze_test_performance çağrıldı, kayıt sayısı: {len(test_records)}")

        topic_stats = defaultdict(lambda: {"correct": 0, "wrong": 0})

        for record in test_records:
            try:
                _, test_json, correct, wrong, _ = record
                test_data = json.loads(test_json)
                for q in test_data:
                    topic = q.get("topic", "GENEL")
                    if q["user_answer"] == q["correct_answer"]:
                        topic_stats[topic]["correct"] += 1
                    else:
                        topic_stats[topic]["wrong"] += 1
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode hatası test kaydında: {record}, hata: {e}")
            except KeyError as e:
                logger.error(f"Anahtar hatası test kaydında: {record}, eksik anahtar: {e}")

        recommendations = {}
        for topic, stats in topic_stats.items():
            total = stats["correct"] + stats["wrong"]
            success_rate = stats["correct"] / total if total > 0 else 0

            if success_rate >= 0.8:
                level = "hard"
            elif success_rate >= 0.5:
                level = "medium"
            else:
                level = "easy"

            recommendations[topic] = {
                "zorluk": level,
                "doğru": stats["correct"],
                "yanlış": stats["wrong"],
                "başarı_oranı": round(success_rate * 100, 1)
            }

        logger.info(f"analyze_test_performance başarıyla tamamlandı. Konu sayısı: {len(recommendations)}")
        return recommendations

    except Exception as e:
        logger.error(f"analyze_test_performance sırasında hata oluştu: {e}", exc_info=True)
        raise
