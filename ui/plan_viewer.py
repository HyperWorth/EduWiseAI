import streamlit as st
import pandas as pd
from utils import pdf_exporter
from datetime import datetime
import json
from logic.question_generator import generate_question_for_topic
from data.db_manager import DBManager
from logger import logger  # logger.py'den import

def show_learning_plan(json_output: dict):
    db = DBManager()
    st.header("🗓️ Öğrenme Planı")

    tum_konular = json_output.get("tum_konular", [])
    calisma_plani = json_output.get("calisma_plani", [])

    df = pd.DataFrame(calisma_plani)
    bugun = datetime.today().date()

    with st.expander("📚 Tüm Konular ve Alt Konular"):
        for konu in tum_konular:
            st.markdown(f"**🔹 {konu['konu']}**")
            for alt in konu["alt_konular"]:
                st.markdown(f"- {alt}")

    st.markdown("### 📋 Günlük Çalışma Planı")
    with st.container():
        for i, row in df.iterrows():
            st.markdown("---")
            col1, col2, col3 = st.columns([3, 3, 1])

            try:
                plan_tarihi = datetime.strptime(row['tarih'], "%Y-%m-%d").date()
            except Exception as e:
                logger.warning(f"Tarih parse hatası: {row.get('tarih')} - {e}")
                plan_tarihi = None

            with col1:
                tarih_gosterimi = f"**{row.get('tarih', '')} - {row.get('konu', '')} / {row.get('alt_konu', '')}**"
                if plan_tarihi == bugun:
                    tarih_gosterimi = "⭐ " + tarih_gosterimi
                st.markdown(tarih_gosterimi)
                st.markdown(f"🎯 Görev: *{row.get('gorev', '')}*")

            with col2:
                st.markdown(f"🧩 Etkinlik: `{row.get('etkinlik', '')}` | 🔁 Tekrar: `{row.get('tekrar', '')}` | 📝 Soru Çöz: `{row.get('soru_coz', '')}`")

            with col3:
                if row.get('soru_coz'):
                    if st.button(f"Test Üret", key=f"test_btn_{i}"):
                        try:
                            st.info("🤖 AI tarafından test oluşturuluyor...")
                            questions = generate_question_for_topic(
                                topic=row.get('gorev', ''),
                                difficulty="medium",
                                count=40
                            )

                            if questions and isinstance(questions, list):
                                db.save_test(user=st.session_state.user, test_json=json.dumps(questions))
                                st.session_state.question_json = questions
                                st.success(f"✅ '{row.get('gorev', '')}' konusu için test üretildi.")
                                logger.info(f"Test başarıyla üretildi: {row.get('gorev', '')}")
                            else:
                                st.error("❌ Soru üretilemedi.")
                                logger.error(f"Soru üretilemedi: {row.get('gorev', '')}")

                        except Exception as e:
                            st.error(f"❌ Test üretirken hata oluştu: {e}")
                            logger.exception(f"Test üretirken hata: {e}")

            st.markdown(" ")


def show_learning_plan_simple(json_output: dict):
    st.header("🗓️ Öğrenme Planı")
    db = DBManager()
    tum_konular = json_output.get("tum_konular", [])
    calisma_plani = json_output.get("calisma_plani", [])

    with st.expander("📚 Tüm Konular ve Alt Konular"):
        for konu in tum_konular:
            st.markdown(f"**🔹 {konu['konu']}**")
            for alt in konu["alt_konular"]:
                st.markdown(f"- {alt}")

    st.subheader("📌 Günlük Plan")
    for i, row in enumerate(calisma_plani):
        st.markdown(f"### 📅 Gün {row.get('gun')}: {row.get('konu')} > {row.get('alt_konu')}")
        st.markdown(f"- **Etkinlik:** {row.get('etkinlik')}")
        st.markdown(f"- **Görev:** {row.get('gorev')}")
        st.markdown(f"- **Tarih:** {row.get('tarih')}")
        st.markdown(f"- **Tekrar:** {'Evet' if row.get('tekrar') else 'Hayır'}")
        st.markdown(f"- **Soru Çözümü:** {'Evet' if row.get('soru_coz') else 'Hayır'}")

        if row.get('soru_coz'):
            unique_key = f"test_btn_{i}_{row.get('gun')}_{row.get('gorev')}"
            if st.button("🧪 Test Üret", key=unique_key):
                try:
                    st.info("🤖 AI tarafından test oluşturuluyor...")
                    questions = generate_question_for_topic(
                        topic=row.get('gorev', ''),
                        difficulty="medium",
                        count=40
                    )
                    if questions and isinstance(questions, list):
                        db.save_test(user=st.session_state.user, test_json=json.dumps(questions))
                        st.session_state.question_json = questions
                        st.success(f"✅ '{row.get('gorev', '')}' konusu için test üretildi.")
                        logger.info(f"Test başarıyla üretildi: {row.get('gorev', '')}")
                    else:
                        st.error("❌ Soru üretilemedi.")
                        logger.error(f"Soru üretilemedi: {row.get('gorev', '')}")
                except Exception as e:
                    st.error(f"❌ Test üretirken hata oluştu: {e}")
                    logger.exception(f"Test üretirken hata: {e}")

            st.markdown("---")


def show_plan(plan_data):
    st.header("📅 Öğrenme Planı")

    for day in plan_data.get("days", []):
        st.subheader(f"Gün {day.get('day')}")
        st.write(day.get("activities"))

    if st.button("📄 PDF olarak indir"):
        try:
            pdf_bytes = pdf_exporter.export_plan_to_pdf(plan_data)
            st.download_button(
                label="Planı PDF olarak indir",
                data=pdf_bytes,
                file_name="calisma_plani.pdf",
                mime="application/pdf"
            )
            logger.info("PDF başarıyla oluşturuldu ve indirme başlatıldı.")
        except Exception as e:
            st.error(f"PDF oluşturulurken hata oluştu: {e}")
            logger.exception(f"PDF oluşturulurken hata: {e}")
