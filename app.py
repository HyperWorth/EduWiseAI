import streamlit as st
from ui import plan_viewer, test_page, dashboard, input_form, history_page
from utils.pdf_exporter import PDFExporter
from data.db_manager import DBManager
from logic.topic_analyzer import analyze_topics_with_weights
from logic.question_generator import generate_question_for_topic, generate_questions_from_analysis
from logic.planner import generate_learning_plan_json, generate_learning_path_json, generate_study_plan_json
import random
import json
from logger import logger  # logger.py'deki logger objesini içe aktar

# Initialize database and PDF exporter
db = DBManager()
pdf_exporter = PDFExporter()

st.set_page_config(page_title="Akıllı Öğrenme Sistemi", layout="wide")
st.title("🎓 Akıllı Öğrenme Planlayıcı + Test Sistemi")

# --- Sidebar Menü ---
st.sidebar.title("📚 Ana Menü")
user = st.sidebar.text_input("👤 Kullanıcı Adınız", value="demo_user")
sayfa = st.sidebar.radio("Sayfa Seç:", [
    "🏁 Plan Oluştur",
    "📅 Planı Görüntüle",
    "📝 Test Üret",
    "🧪 Test Çöz",
    "📈 Dashboard",
    "🧩 Zorluk Analizi",
    "📄 PDF İndir",
    "📂 Geçmiş"
])

# Global oturum durumu
if "plan_json" not in st.session_state:
    st.session_state.plan_json = None

if "question_json" not in st.session_state:
    st.session_state.question_json = None

if "user" not in st.session_state:
    st.session_state.user = user
else:
    st.session_state.user = user

# --- Sayfa Yönlendirme ---
if sayfa == "🏁 Plan Oluştur":
    user_inputs = input_form.get_user_inputs()
    if user_inputs:
        st.success("🧠 AI destekli plan oluşturuluyor...")
        try:
            path_data_str = generate_learning_path_json(
                user_topic=user_inputs["topic"],
                user_level=user_inputs["level"]
            )
            path_data = json.loads(path_data_str)
            tum_konular = path_data.get("tum_konular", [])
            baglantilar = path_data.get("baglantilar", [])

            if not tum_konular or not baglantilar:
                st.error("❌ Yol haritası oluşturulamadı. Lütfen girdi bilgilerini kontrol edin.")
                logger.error("Yol haritası oluşturulamadı: tum_konular veya baglantilar boş.")
                st.stop()

            study_plan_str = generate_study_plan_json(
                tum_konular=tum_konular,
                baglantilar=baglantilar,
                daily_minutes=user_inputs["daily_minutes"],
                start_date=user_inputs["start_date"],
                duration_days=user_inputs["duration_days"]
            )
            study_plan = json.loads(study_plan_str)

            if "calisma_plani" not in study_plan:
                st.error("❌ Çalışma planı oluşturulamadı.")
                logger.error("Çalışma planı oluşturulamadı: 'calisma_plani' yok.")
                st.stop()

            full_plan = {
                "tum_konular": tum_konular,
                "baglantilar": baglantilar,
                "calisma_plani": study_plan["calisma_plani"]
            }

            st.session_state.plan_json = full_plan
            st.success("✅ Plan başarıyla oluşturuldu.")

            plan_str = json.dumps(full_plan, ensure_ascii=False, indent=2)
            db.save_plan(user, plan_str)
            logger.info(f"Plan başarıyla kaydedildi kullanıcı: {user}")

        except Exception as e:
            st.error(f"🚨 Bir hata oluştu: {e}")
            logger.error(f"Plan oluşturma hatası: {e}", exc_info=True)
            st.stop()

elif sayfa == "📅 Planı Görüntüle":
    if st.session_state.plan_json:
        plan_viewer.show_learning_plan(st.session_state.plan_json)
    else:
        st.warning("Henüz bir plan oluşturulmadı.")

elif sayfa == "🧪 Test Çöz":
    if st.session_state.question_json:
        test_page.run_test_page(st.session_state.question_json)
    else:
        st.warning("Henüz test verisi yüklenmedi.")

elif sayfa == "📝 Test Üret":
    st.header("📝 AI Destekli Test Üretimi")
    topic = st.text_input("🧠 Konu girin:", value="Simple Past Tense")
    difficulty = st.selectbox("🧩 Zorluk seviyesi:", ["easy", "medium", "hard"])
    question_count = st.slider("🧪 Soru sayısı", min_value=1, max_value=40, value=5)

    if st.button("🚀 Testi Oluştur"):
        st.info("🤖 AI tarafından test oluşturuluyor...")
        try:
            questions = generate_question_for_topic(topic=topic, difficulty=difficulty, count=question_count)

            if not questions or not isinstance(questions, list):
                st.error("❌ Soru üretilemedi. Lütfen daha sonra tekrar deneyin.")
                logger.error(f"Soru üretilemedi topic={topic}, difficulty={difficulty}, count={question_count}")
            else:
                db.save_test(user=user, test_json=json.dumps(questions))
                st.session_state.question_json = questions
                st.success("✅ Test başarıyla oluşturuldu. Artık '🧪 Test Çöz' sayfasında çözebilirsiniz.")
                logger.info(f"Test başarıyla oluşturuldu kullanıcı: {user}, konu: {topic}")

        except Exception as e:
            st.error(f"❌ Hata oluştu: {e}")
            logger.error(f"Test üretim hatası: {e}", exc_info=True)

elif sayfa == "📈 Dashboard":
    test_records = db.get_all_test_results(user)
    if test_records:
        dates = [rec[5][:10] for rec in test_records]
        corrects = [rec[3] for rec in test_records]
        wrongs = [rec[4] for rec in test_records]
        total = [c + w for c, w in zip(corrects, wrongs)]
        actual_minutes = [min(60, 15 * t) for t in total]
        target_minutes = [60] * len(actual_minutes)

        difficulty_stats = db.get_difficulty_breakdown(user)
        topic_data = db.get_topic_minutes_estimate(user)

        dashboard.show_dashboard(
            user_name=user,
            target_minutes=target_minutes,
            actual_minutes=actual_minutes,
            dates=dates,
            topic_data=topic_data,
            correct=sum(corrects),
            wrong=sum(wrongs),
            difficulty_stats=difficulty_stats
        )
    else:
        st.info("Henüz geçmiş test verisi yok.")

elif sayfa == "🧩 Zorluk Analizi":
    st.header("🧩 AI Destekli Zorluk Analizi")

    if "difficulty_analysis" not in st.session_state:
        st.session_state.difficulty_analysis = None

    if st.button("📊 Analizi Başlat"):
        try:
            test_records = db.get_all_test_results(user)
            analysis = analyze_topics_with_weights(test_records)

            if not analysis:
                st.warning("Analiz için yeterli veri bulunamadı. En az birkaç konudan 5+ soru çözmelisiniz.")
                logger.warning("Zorluk analizi için yeterli veri yok.")
            elif all(item["success_rate"] == 100.0 for item in analysis):
                st.info("Tüm konularda başarı oranı %100. Tebrikler! Zayıf konu bulunamadı.")
                logger.info("Zorluk analizi: tüm konularda başarı %100")
            elif sum(item["weight"] for item in analysis) == 0:
                st.warning("Konular arası başarı oranları eşit. Ağırlıklı test üretilemez.")
                logger.warning("Zorluk analizi: ağırlıklar sıfır")
            else:
                st.session_state.difficulty_analysis = analysis
                st.success("✅ Analiz tamamlandı.")
                logger.info("Zorluk analizi tamamlandı.")

        except Exception as e:
            st.error(f"❌ Analiz sırasında hata oluştu: {e}")
            logger.error(f"Zorluk analizi hatası: {e}", exc_info=True)

    if st.session_state.difficulty_analysis:
        st.table(st.session_state.difficulty_analysis)

        st.subheader("🎯 Bu analizlere göre test üretmek ister misiniz?")
        total_questions = st.slider("Soru Sayısı", min_value=1, max_value=40, value=5)

        if st.button("🚀 Soru Üret"):
            try:
                if sum(item["weight"] for item in st.session_state.difficulty_analysis) == 0:
                    st.error("⚠️ Ağırlıklar sıfır. Lütfen daha çeşitli başarı oranlarıyla test çözün.")
                    logger.warning("Test üretim denemesi: ağırlıklar sıfır.")
                else:
                    st.info("🤖 AI tarafından test oluşturuluyor...")
                    generated_questions = generate_questions_from_analysis(
                        st.session_state.difficulty_analysis, total_questions
                    )

                    if generated_questions:
                        db.save_test(user=user, test_json=json.dumps(generated_questions))
                        st.session_state.question_json = generated_questions
                        st.success("✅ Test başarıyla oluşturuldu. Artık '🧪 Test Çöz' sayfasında çözebilirsiniz.")
                        logger.info(f"Zorluk analizinden test üretildi kullanıcı: {user}")
                    else:
                        st.error("❌ AI tarafından soru üretilemedi. Lütfen tekrar deneyin.")
                        logger.error("AI tarafından soru üretilemedi zorluk analizi sonrası.")
            except Exception as e:
                st.error(f"❌ Test üretirken hata oluştu: {e}")
                logger.error(f"Test üretim hatası zorluk analizinden: {e}", exc_info=True)

elif sayfa == "📄 PDF İndir":
    if st.session_state.plan_json:
        try:
            pdf_bytes = pdf_exporter.export_plan_to_pdf(st.session_state.plan_json)
            st.download_button(
                label="📄 Planı PDF olarak indir",
                data=pdf_bytes,
                file_name="calisma_plani.pdf",
                mime="application/pdf"
            )
            logger.info(f"PDF indirildi kullanıcı: {user}")
        except Exception as e:
            st.error(f"❌ PDF oluşturulurken hata oluştu: {e}")
            logger.error(f"PDF oluşturma hatası: {e}", exc_info=True)
    else:
        st.info("Plan PDF'e dönüştürülmek için hazır değil.")

elif sayfa == "📂 Geçmiş":
    try:
        history_page.show_history(user)
        logger.info(f"Geçmiş görüntülendi kullanıcı: {user}")
    except Exception as e:
        st.error(f"❌ Geçmiş sayfası yüklenirken hata oluştu: {e}")
        logger.error(f"Geçmiş sayfası hatası: {e}", exc_info=True)
