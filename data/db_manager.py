import sqlite3
from datetime import datetime
from logic.topic_analyzer import analyze_topics_with_weights
import json
from logger import logger  # Logger import edildi

class DBManager:
    def __init__(self, db_path="data/app_data.db"):
        try:
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.create_tables()
            logger.info(f"DB bağlantısı kuruldu: {db_path}")
        except Exception as e:
            logger.error(f"DB bağlantısı sırasında hata: {e}", exc_info=True)
            raise

    def create_tables(self):
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    plan_json TEXT,
                    created_at TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    test_json TEXT,
                    created_at TEXT
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    test_json TEXT,
                    correct INTEGER,
                    wrong INTEGER,
                    timestamp TEXT
                )
            """)

            self.conn.commit()
            logger.info("Tablolar başarıyla oluşturuldu veya mevcut.")
        except Exception as e:
            logger.error(f"Tablo oluşturma sırasında hata: {e}", exc_info=True)
            raise

    def save_plan(self, user, plan_json):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO plans (user, plan_json, created_at)
                VALUES (?, ?, ?)
            """, (user, plan_json, datetime.now().isoformat()))
            self.conn.commit()
            logger.info(f"Plan kaydedildi - Kullanıcı: {user}")
        except Exception as e:
            logger.error(f"Plan kaydetme hatası - Kullanıcı: {user}, Hata: {e}", exc_info=True)
            raise

    def save_test(self, user, test_json):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO tests (user, test_json, created_at)
                VALUES (?, ?, ?)
            """, (user, test_json, datetime.now().isoformat()))
            self.conn.commit()
            logger.info(f"Test kaydedildi - Kullanıcı: {user}")
        except Exception as e:
            logger.error(f"Test kaydetme hatası - Kullanıcı: {user}, Hata: {e}", exc_info=True)
            raise

    def save_test_result(self, user, test_json, correct, wrong):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO test_results (user, test_json, correct, wrong, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (user, test_json, correct, wrong, datetime.now().isoformat()))
            self.conn.commit()
            logger.info(f"Test sonucu kaydedildi - Kullanıcı: {user}, Doğru: {correct}, Yanlış: {wrong}")
        except Exception as e:
            logger.error(f"Test sonucu kaydetme hatası - Kullanıcı: {user}, Hata: {e}", exc_info=True)
            raise

    def get_latest_plan(self, user):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT plan_json, created_at FROM plans
                WHERE user = ?
                ORDER BY created_at DESC LIMIT 1
            """, (user,))
            result = cursor.fetchone()
            logger.info(f"Son plan alındı - Kullanıcı: {user}")
            return result
        except Exception as e:
            logger.error(f"Son plan alınırken hata - Kullanıcı: {user}, Hata: {e}", exc_info=True)
            raise

    def get_all_plans(self, user):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, plan_json, created_at FROM plans
                WHERE user = ?
                ORDER BY created_at DESC
            """, (user,))
            result = cursor.fetchall()
            logger.info(f"Tüm planlar alındı - Kullanıcı: {user}")
            return result
        except Exception as e:
            logger.error(f"Tüm planlar alınırken hata - Kullanıcı: {user}, Hata: {e}", exc_info=True)
            raise

    def get_all_tests_from_tests(self, user):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, test_json, created_at FROM tests
                WHERE user = ?
                ORDER BY created_at DESC
            """, (user,))
            result = cursor.fetchall()
            logger.info(f"Tüm testler alındı - Kullanıcı: {user}")
            return result
        except Exception as e:
            logger.error(f"Tüm testler alınırken hata - Kullanıcı: {user}, Hata: {e}", exc_info=True)
            raise

    def get_all_test_results(self, user):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM test_results WHERE user = ?", (user,))
            result = cursor.fetchall()
            logger.info(f"Tüm test sonuçları alındı - Kullanıcı: {user}")
            return result
        except Exception as e:
            logger.error(f"Tüm test sonuçları alınırken hata - Kullanıcı: {user}, Hata: {e}", exc_info=True)
            raise

    def get_all_test_results_specific(self, user):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, test_json, correct, wrong, timestamp FROM test_results WHERE user = ?", (user,))
            result = cursor.fetchall()
            logger.info(f"Özel test sonuçları alındı - Kullanıcı: {user}")
            return result
        except Exception as e:
            logger.error(f"Özel test sonuçları alınırken hata - Kullanıcı: {user}, Hata: {e}", exc_info=True)
            raise

    def delete_plan(self, plan_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM plans WHERE id = ?", (plan_id,))
            self.conn.commit()
            logger.info(f"Plan silindi - Plan ID: {plan_id}")
        except Exception as e:
            logger.error(f"Plan silme hatası - Plan ID: {plan_id}, Hata: {e}", exc_info=True)
            raise

    def delete_test(self, test_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM tests WHERE id = ?", (test_id,))
            self.conn.commit()
            logger.info(f"Test silindi - Test ID: {test_id}")
        except Exception as e:
            logger.error(f"Test silme hatası - Test ID: {test_id}, Hata: {e}", exc_info=True)
            raise

    def delete_test_results(self, test_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM test_results WHERE id = ?", (test_id,))
            self.conn.commit()
            logger.info(f"Test sonucu silindi - Test Result ID: {test_id}")
        except Exception as e:
            logger.error(f"Test sonucu silme hatası - Test Result ID: {test_id}, Hata: {e}", exc_info=True)
            raise

    def get_user_topic_analysis(self, user):
        try:
            records = self.get_all_test_results(user)
            if not records:
                logger.info(f"Kullanıcı için test sonucu bulunamadı - Kullanıcı: {user}")
                return []
            analysis = analyze_topics_with_weights(records)
            logger.info(f"Konu analizi yapıldı - Kullanıcı: {user}")
            return analysis
        except Exception as e:
            logger.error(f"Konu analizi sırasında hata - Kullanıcı: {user}, Hata: {e}", exc_info=True)
            raise

    def get_difficulty_breakdown(self, user):
        try:
            records = self.get_all_test_results(user)
            difficulty_counts = {
                "easy": {"doğru": 0, "yanlış": 0},
                "medium": {"doğru": 0, "yanlış": 0},
                "hard": {"doğru": 0, "yanlış": 0}
            }

            for _, _, test_json, _, _, _ in records:
                try:
                    test = json.loads(test_json)
                    for q in test:
                        difficulty = q.get("difficulty", "medium")
                        if difficulty not in difficulty_counts:
                            continue

                        user_answer = q.get("user_answer")
                        correct_answer = q.get("correct_answer")

                        if user_answer is None or correct_answer is None:
                            continue

                        if user_answer == correct_answer:
                            difficulty_counts[difficulty]["doğru"] += 1
                        else:
                            difficulty_counts[difficulty]["yanlış"] += 1

                except Exception as e:
                    logger.warning(f"Test verisi işlenirken hata - Kullanıcı: {user}, Hata: {e}")
                    continue

            logger.info(f"Zorluk dağılımı hesaplandı - Kullanıcı: {user}")
            return difficulty_counts
        except Exception as e:
            logger.error(f"Zorluk dağılımı alınırken hata - Kullanıcı: {user}, Hata: {e}", exc_info=True)
            raise

    def get_topic_minutes_estimate(self, user):
        try:
            records = self.get_all_test_results(user)
            topic_minutes = {}

            for _, _, test_json, _, _, _ in records:
                try:
                    test = json.loads(test_json)
                    for q in test:
                        topic = q.get("topic", "Bilinmeyen")
                        topic_minutes[topic] = topic_minutes.get(topic, 0) + 2  # 1 soru ≈ 2 dk
                except Exception as e:
                    logger.warning(f"Test verisi işlenirken hata (dakika tahmini) - Kullanıcı: {user}, Hata: {e}")
                    continue

            logger.info(f"Konu dakika tahmini yapıldı - Kullanıcı: {user}")
            return topic_minutes
        except Exception as e:
            logger.error(f"Konu dakika tahmini alınırken hata - Kullanıcı: {user}, Hata: {e}", exc_info=True)
            raise
