import json
from logic.gemini_api import call_gemini_json_response
from logger import logger


def generate_learning_plan_json(user_topic: str, user_level: str, daily_minutes: int, start_date: str, duration_days: int) -> str:
    try:
        logger.info(f"generate_learning_plan_json çağrıldı: topic={user_topic}, level={user_level}, daily_minutes={daily_minutes}, start_date={start_date}, duration_days={duration_days}")
        
        prompt = f"""
Bir kullanıcı "{user_topic}" öğrenmek istiyor.
Bu kullanıcı:
- Seviyesi: {user_level}
- Günde {daily_minutes} dakika çalışabiliyor
- Başlangıç tarihi: {start_date}
- Süre: {duration_days} gün

Senin görevin:

1. Bu konuda öğrenilmesi gereken tüm temel konuları ve alt konuları belirle. (tum_konular)
2. Hangi konuların hangi ön koşullara bağlı olduğunu belirt. (baglantilar)
3. Verilen süreye uygun bir günlük çalışma planı üret. (calisma_plani)

Her gün için şunları belirt:
- Gün numarası ve tarih
- Konu ve alt konu
- Etkinlik türü (video, okuma, quiz, tekrar, soru çözümü)
- Günlük görev (örnek: "10 cümle yaz", "5 kelime ezberle")
- Tekrar var mı? Soru çözümü var mı?

Yalnızca aşağıdaki JSON formatında çıktı üret.
"""

        system_instruction = "Yalnızca aşağıdaki formatta JSON çıktısı ver. Plan yapısı sistematik ve öğrenmeye uygun olmalı."

        output_schema = {
            "type": "object",
            "required": ["tum_konular", "baglantilar", "calisma_plani"],
            "properties": {
                "tum_konular": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["konu", "alt_konular"],
                        "properties": {
                            "konu": {"type": "string"},
                            "alt_konular": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                },
                "baglantilar": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["konu", "once_gelmesi_gerekenler"],
                        "properties": {
                            "konu": {"type": "string"},
                            "once_gelmesi_gerekenler": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                },
                "calisma_plani": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["gun", "tarih", "konu", "alt_konu", "etkinlik", "gorev", "tekrar", "soru_coz"],
                        "properties": {
                            "gun": {"type": "integer"},
                            "tarih": {"type": "string"},
                            "konu": {"type": "string"},
                            "alt_konu": {"type": "string"},
                            "etkinlik": {"type": "string"},
                            "gorev": {"type": "string"},
                            "tekrar": {"type": "boolean"},
                            "soru_coz": {"type": "boolean"}
                        }
                    }
                }
            }
        }

        result = call_gemini_json_response(prompt, system_instruction, output_schema)
        logger.info("generate_learning_plan_json başarıyla tamamlandı.")
        return result

    except Exception as e:
        logger.error(f"generate_learning_plan_json sırasında hata oluştu: {e}", exc_info=True)
        raise


def generate_learning_path_json(user_topic: str, user_level: str) -> dict:
    try:
        logger.info(f"generate_learning_path_json çağrıldı: topic={user_topic}, level={user_level}")
        
        prompt = f"""
Bir kullanıcı "{user_topic}" öğrenmek istiyor.
- Seviyesi: {user_level}

Senin görevin:
1. Bu konuda öğrenilmesi gereken tüm temel konuları ve alt konuları belirle. (tum_konular)
2. Hangi konuların hangi ön koşullara bağlı olduğunu belirt. (baglantilar)

Yalnızca aşağıdaki JSON formatında çıktı üret.
"""
        system_instruction = "Sadece 'tum_konular' ve 'baglantilar' alanlarını içeren bir JSON çıktısı ver."

        output_schema = {
            "type": "object",
            "required": ["tum_konular", "baglantilar"],
            "properties": {
                "tum_konular": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["konu", "alt_konular"],
                        "properties": {
                            "konu": {"type": "string"},
                            "alt_konular": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                },
                "baglantilar": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["konu", "once_gelmesi_gerekenler"],
                        "properties": {
                            "konu": {"type": "string"},
                            "once_gelmesi_gerekenler": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }

        result = call_gemini_json_response(prompt, system_instruction, output_schema)
        logger.info("generate_learning_path_json başarıyla tamamlandı.")
        return result

    except Exception as e:
        logger.error(f"generate_learning_path_json sırasında hata oluştu: {e}", exc_info=True)
        raise


def generate_study_plan_json(tum_konular: list, baglantilar: list, daily_minutes: int, start_date: str, duration_days: int) -> dict:
    try:
        logger.info(f"generate_study_plan_json çağrıldı: daily_minutes={daily_minutes}, start_date={start_date}, duration_days={duration_days}")
        
        prompt = f"""
Bir kullanıcı öğrenmeye başlıyor.
- Günlük {daily_minutes} dakika çalışabiliyor.
- Başlangıç tarihi: {start_date}
- Toplam süre: {duration_days} gün

Kullanıcı için daha önce hazırlanmış bir konu listesi ve bağlantılar şunlardır:

Tüm Konular:
{tum_konular}

Bağlantılar:
{baglantilar}

Senin görevin:
Verilen süreye uygun bir günlük çalışma planı üret. (calisma_plani)

Her gün için şunları belirt:
- Gün numarası ve tarih
- Konu ve alt konu
- Etkinlik türü (video, okuma, quiz, tekrar, soru çözümü)
- Günlük görev (örnek: "10 cümle yaz", "5 kelime ezberle")
- Tekrar var mı? Soru çözümü var mı?

Sadece aşağıdaki JSON formatında çıktı ver.
"""
        system_instruction = "Sadece 'calisma_plani' alanını içeren bir JSON çıktısı ver."

        output_schema = {
            "type": "object",
            "required": ["calisma_plani"],
            "properties": {
                "calisma_plani": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["gun", "tarih", "konu", "alt_konu", "etkinlik", "gorev", "tekrar", "soru_coz"],
                        "properties": {
                            "gun": {"type": "integer"},
                            "tarih": {"type": "string"},
                            "konu": {"type": "string"},
                            "alt_konu": {"type": "string"},
                            "etkinlik": {"type": "string"},
                            "gorev": {"type": "string"},
                            "tekrar": {"type": "boolean"},
                            "soru_coz": {"type": "boolean"}
                        }
                    }
                }
            }
        }

        result = call_gemini_json_response(prompt, system_instruction, output_schema)
        logger.info("generate_study_plan_json başarıyla tamamlandı.")
        return result

    except Exception as e:
        logger.error(f"generate_study_plan_json sırasında hata oluştu: {e}", exc_info=True)
        raise
