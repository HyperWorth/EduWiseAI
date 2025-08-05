import streamlit as st
from utils import pdf_exporter, chart_utils
from data.db_manager import DBManager
import json
from logger import logger  # logger.py'den import

def run_test_page(questions_data):
    st.header("📝 Test Çöz")
    user_answers = {}

    try:
        questions = questions_data  # ✅ direkt liste olarak ele alıyoruz
        logger.info(f"Test sayfası için {len(questions)} soru yüklendi.")

        for idx, q in enumerate(questions):
            st.markdown(f"**{idx + 1}. {q['question']}**")
            user_answers[idx] = st.radio(
                "Cevabınızı seçin:",
                options=q["options"],
                key=f"q_{idx}"
            )
            st.markdown("---")

        if st.button("📊 Testi Bitir ve Sonuçları Gör"):
            correct = 0
            wrong = 0
            
            for idx, q in enumerate(questions):
                user_ans = user_answers.get(idx)
                # Kullanıcı cevabı seçmedi ise hata önleme
                if not user_ans or len(user_ans) == 0:
                    st.warning(f"{idx+1}. soruya cevap vermediniz.")
                    logger.warning(f"Kullanıcı {idx+1}. soruya cevap vermedi.")
                    continue

                questions[idx]["user_answer"] = user_ans[0]  # 💾 kullanıcı cevabını ekle
                if user_ans[0] == q["correct_answer"]:
                    correct += 1
                else:
                    wrong += 1

            logger.info(f"Test tamamlandı. Doğru: {correct}, Yanlış: {wrong}")

            try:
                db = DBManager()
                db.save_test_result(
                    user=st.session_state.user,
                    test_json=json.dumps(questions),
                    correct=correct,
                    wrong=wrong
                )
                logger.info("Test sonucu başarıyla veritabanına kaydedildi.")
            except Exception as e:
                logger.exception(f"Test sonucu veritabanına kaydedilemedi: {e}")
                st.error("Test sonucu veritabanına kaydedilirken hata oluştu.")

            st.success(f"✅ Doğru: {correct}")
            st.error(f"❌ Yanlış: {wrong}")

            st.subheader("📘 Çözümler")
            for idx, q in enumerate(questions):
                st.markdown(f"**Soru {idx + 1}:** {q['question']}")
                if q.get("user_answer") == q["correct_answer"]:
                    st.markdown(f"- ✅ Doğru Cevap: {q['correct_answer']}")
                else:
                    st.markdown(f"- ❌ Kullanıcının Cevap: {q.get('user_answer', 'Cevap yok')}")
                    st.markdown(f"- ✅ Doğru Cevap: {q['correct_answer']}")
                
                st.markdown(f"- ℹ️ Açıklama: {q['explanation']}")
                st.markdown("---")

    except Exception as e:
        logger.exception(f"Test sayfasında beklenmedik hata oluştu: {e}")
        st.error("Bir hata oluştu. Lütfen sayfayı yenileyip tekrar deneyin.")
