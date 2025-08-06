import streamlit as st
from data.db_manager import DBManager
import json
from ui import plan_viewer
from logger import logger  # logger'ı ekleyelim

db = DBManager()

def show_history(user):
    st.title("📚 Geçmiş Planlar ve Testler")

    try:
        st.subheader("📅 Geçmiş Öğrenme Planları")
        plans = db.get_all_plans(user)
    except Exception as e:
        st.error(f"❌ Planlar yüklenirken hata oluştu: {e}")
        logger.exception(f"Planlar yüklenirken hata: {e}")
        plans = []

    if not plans:
        st.info("Hiç plan bulunamadı.")
    else:
        for plan_id, plan_json, created_at in plans:
            st.markdown(f"**🕒 Oluşturulma Tarihi:** `{created_at}`")
            try:
                plan_data = json.loads(plan_json)
                with st.expander("📚 Öğrenme Planı"):
                    plan_viewer.show_learning_plan_simple(plan_data)
            except Exception as e:
                st.error(f"❌ Plan gösterilirken hata oluştu: {e}")
                logger.exception(f"Plan gösterilirken hata: {e}")

            if st.button(f"🗑️ Sil (Plan #{plan_id})", key=f"del_plan_{plan_id}"):
                try:
                    db.delete_plan(plan_id)
                    st.success("Plan silindi!")
                    logger.info(f"Plan #{plan_id} silindi, kullanıcı: {user}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Plan silinirken hata oluştu: {e}")
                    logger.exception(f"Plan silinirken hata: {e}")

    st.markdown("---")

    try:
        st.subheader("🧪 Test Geçmişi")
        tests = db.get_all_test_results_specific(user)
    except Exception as e:
        st.error(f"❌ Test geçmişi yüklenirken hata oluştu: {e}")
        logger.exception(f"Test geçmişi yüklenirken hata: {e}")
        tests = []

    if not tests:
        st.info("Hiç test çözülmemiş.")
    else:
        for test_id, test_json, correct, wrong, created_at in tests:
            st.markdown(f"**📅 Tarih:** `{created_at}` – ✅ {correct} | ❌ {wrong}")
            try:
                with st.expander(f"📄 Test Detayları (#{test_id})"):
                    test_data = json.loads(test_json)
                    for idx, q in enumerate(test_data):
                        st.markdown(f"**Soru {idx + 1}:** {q['question']}")
                        if q.get("user_answer") == q["correct_answer"]:
                            st.markdown(f"- ✅ Doğru Cevap: {q['correct_answer']}")
                        else:
                            st.markdown(f"- ❌ Kullanıcının Cevap: {q.get('user_answer', 'Cevap yok')}")
                            st.markdown(f"- ✅ Doğru Cevap: {q['correct_answer']}")
                        st.markdown(f"- ℹ️ Açıklama: {q['explanation']}")
                        st.markdown("---")
            except Exception as e:
                st.error(f"❌ Test detayları yüklenirken hata oluştu: {e}")
                logger.exception(f"Test detayları yüklenirken hata: {e}")

            if st.button(f"🗑️ Sil (Test #{test_id})", key=f"del_test_{test_id}"):
                try:
                    db.delete_test_results(test_id)
                    st.success("Test silindi!")
                    logger.info(f"Test #{test_id} silindi, kullanıcı: {user}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Test silinirken hata oluştu: {e}")
                    logger.exception(f"Test silinirken hata: {e}")
