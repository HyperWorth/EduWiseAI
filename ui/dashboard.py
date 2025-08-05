import streamlit as st
from utils import chart_utils
from datetime import datetime
import random
from logger import logger  # Logger import edildi

# Opsiyonel: günlük motivasyon mesajları listesi
MOTIVATION_QUOTES = [
    "Bugün küçük bir adım, yarın büyük bir fark yaratır. 🚀",
    "Vazgeçme! Zorluklar başarıya giden yoldaki işaretlerdir. 💪",
    "Sadece başla. Mükemmellik zamanla gelir. ⏳",
    "Her gün 1% ilerle, 1 yıl sonunda %37 daha iyi olursun. 📈",
    "Sen çalıştıkça başarı senden kaçamaz. 🔥"
]

def get_daily_motivation():
    quote = random.choice(MOTIVATION_QUOTES)
    logger.debug(f"Motivasyon mesajı seçildi: {quote}")
    return quote

def show_dashboard(
    user_name: str,
    target_minutes: list,
    actual_minutes: list,
    dates: list,
    topic_data: list,
    correct: int,
    wrong: int,
    difficulty_stats: dict
):
    logger.info(f"Dashboard gösteriliyor: Kullanıcı = {user_name}")
    
    try:
        st.title("📊 Öğrenme Dashboard")
        
        st.subheader(f"Merhaba, {user_name} 👋")
        st.success(f"🎯 Bugünün Hedefi: {target_minutes[-1]} dakika çalışmak.")
        st.info(f"💡 Motivasyon: {get_daily_motivation()}")

        logger.debug("Günlük ilerleme grafiği oluşturuluyor.")
        st.markdown("---")
        st.subheader("Günlük Çalışma İlerlemesi")
        st.plotly_chart(chart_utils.plot_daily_progress(dates, target_minutes, actual_minutes), use_container_width=True)

        logger.debug("Konu dağılım grafiği oluşturuluyor.")
        st.markdown("---")
        st.subheader("Konu Bazlı Dağılım")
        st.plotly_chart(chart_utils.plot_topic_distribution(topic_data), use_container_width=True)

        logger.debug("Test performansı grafikleri oluşturuluyor.")
        st.markdown("---")
        st.subheader("Test Performansı")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(chart_utils.plot_answer_stats(correct, wrong), use_container_width=True)
        with col2:
            st.plotly_chart(chart_utils.plot_difficulty_success(difficulty_stats), use_container_width=True)

        st.markdown("---")
        date_str = datetime.now().strftime('%d %B %Y')
        st.caption(f"🗓️ {date_str} itibariyle güncellenmiştir.")

        logger.info(f"Dashboard başarıyla gösterildi: {user_name} - Tarih: {date_str}")
    
    except Exception as e:
        logger.exception(f"Dashboard gösterilirken hata oluştu: {e}")
        st.error("Bir hata oluştu, lütfen daha sonra tekrar deneyin.")
