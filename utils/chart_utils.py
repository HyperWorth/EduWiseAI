import logging
import plotly.graph_objects as go
import plotly.express as px

from logger import logger  # Logger importu (senin logger.py'den)

def plot_daily_progress(dates, target_minutes, actual_minutes):
    logger.info("Günlük çalışma süresi grafiği oluşturuluyor.")
    try:
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Hedef Süre", x=dates, y=target_minutes, marker_color="lightblue"))
        fig.add_trace(go.Bar(name="Gerçekleşen Süre", x=dates, y=actual_minutes, marker_color="orange"))
        fig.update_layout(
            title="📅 Günlük Çalışma Süresi",
            xaxis_title="Tarih",
            yaxis_title="Dakika",
            barmode="group",
            height=400
        )
        logger.info("Günlük çalışma süresi grafiği başarıyla oluşturuldu.")
        return fig
    except Exception as e:
        logger.exception(f"Günlük çalışma süresi grafiği oluşturulurken hata oluştu: {e}")
        raise

def plot_topic_distribution(topic_data):
    logger.info("Konu bazlı çalışma dağılımı grafiği oluşturuluyor.")
    try:
        labels = list(topic_data.keys())
        values = list(topic_data.values())

        fig = go.Figure(
            data=[go.Pie(labels=labels, values=values, hole=0.4)]
        )
        fig.update_layout(
            title="📘 Konulara Göre Çalışma Dağılımı"
        )
        logger.info("Konu bazlı çalışma dağılımı grafiği başarıyla oluşturuldu.")
        return fig
    except Exception as e:
        logger.exception(f"Konu bazlı çalışma dağılımı grafiği oluşturulurken hata oluştu: {e}")
        raise

def plot_answer_stats(correct_count, wrong_count):
    logger.info("Soru başarı analizi grafiği oluşturuluyor.")
    try:
        fig = go.Figure(go.Bar(
            x=["Doğru", "Yanlış"],
            y=[correct_count, wrong_count],
            marker_color=["green", "red"]
        ))
        fig.update_layout(
            title="🧪 Test Sonucu: Doğru/Yanlış",
            yaxis_title="Soru Sayısı"
        )
        logger.info("Soru başarı analizi grafiği başarıyla oluşturuldu.")
        return fig
    except Exception as e:
        logger.exception(f"Soru başarı analizi grafiği oluşturulurken hata oluştu: {e}")
        raise

def plot_difficulty_success(stats):
    logger.info("Zorluk seviyesine göre başarı grafiği oluşturuluyor.")
    try:
        difficulties = []
        correct = []
        wrong = []

        for zorluk, values in stats.items():
            difficulties.append(zorluk.capitalize())
            correct.append(values["doğru"])
            wrong.append(values["yanlış"])

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Doğru", x=difficulties, y=correct, marker_color="green"))
        fig.add_trace(go.Bar(name="Yanlış", x=difficulties, y=wrong, marker_color="crimson"))
        fig.update_layout(
            title="🎯 Zorluk Seviyesine Göre Başarı",
            barmode="group"
        )
        logger.info("Zorluk seviyesine göre başarı grafiği başarıyla oluşturuldu.")
        return fig
    except Exception as e:
        logger.exception(f"Zorluk seviyesine göre başarı grafiği oluşturulurken hata oluştu: {e}")
        raise
