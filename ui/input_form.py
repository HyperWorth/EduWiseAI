import streamlit as st
from datetime import date
from logger import logger  # logger'ı ekleyelim

def get_user_inputs():
    st.header("📚 Öğrenme Hedefini Belirle")

    topic = st.text_input("🔍 Ne öğrenmek istiyorsun?", "İngilizce Zamanlar")
    level = st.radio("📈 Mevcut seviyen", ["Başlangıç", "Orta", "İleri"])
    daily_minutes = st.slider("⏰ Günde kaç dakika ayırabilirsin?", 15, 240, 60, step=15)
    start_date = st.date_input("📅 Başlangıç tarihi", date.today())
    duration_days = st.number_input("📆 Kaç gün çalışmak istiyorsun?", 1, 365, 14)

    if st.button("✅ Plan Oluştur"):
        try:
            user_input = {
                "topic": topic,
                "level": level,
                "daily_minutes": daily_minutes,
                "start_date": str(start_date),
                "duration_days": duration_days
            }
            logger.info(f"Kullanıcı plan girdi oluşturdu: {user_input}")
            return user_input
        except Exception as e:
            st.error(f"❌ Girdi alınırken hata oluştu: {e}")
            logger.exception(f"Girdi alınırken hata: {e}")

    return None
