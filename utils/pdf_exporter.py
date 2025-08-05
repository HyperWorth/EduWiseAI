import logging
from reportlab.lib.pagesizes import A4 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from io import BytesIO
from datetime import datetime

# logger.py'den import ettiğimizi varsayıyorum
from logger import logger

class PDFExporter:
    def __init__(self, title="📘 Öğrenme Planı ve Soru Seti", font_dir="fonts"):
        self.title = title
        self.font_dir = font_dir
        try:
            self._register_fonts()
            logger.info("Fontlar başarıyla yüklendi.")
        except AssertionError as e:
            logger.error(f"Font yüklenirken hata oluştu: {e}")
            raise
        except Exception as e:
            logger.exception(f"Beklenmeyen bir hata oluştu: {e}")
            raise

    def _register_fonts(self):
        font_path_regular = os.path.join(self.font_dir, "DejaVuSans.ttf")
        font_path_bold = os.path.join(self.font_dir, "DejaVuSans-Bold.ttf")

        assert os.path.exists(font_path_regular), f"Font bulunamadı: {font_path_regular}"
        assert os.path.exists(font_path_bold), f"Font bulunamadı: {font_path_bold}"

        pdfmetrics.registerFont(TTFont("DejaVu", font_path_regular))
        pdfmetrics.registerFont(TTFont("DejaVu-Bold", font_path_bold))

    def export_plan_to_pdf(self, plan_data):
        logger.info("PDF oluşturma işlemi başladı.")
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer, pagesize=A4,
                leftMargin=2*cm, rightMargin=2*cm,
                topMargin=2*cm, bottomMargin=2*cm
            )

            styles = getSampleStyleSheet()

            title_style = ParagraphStyle('TitleStyle', parent=styles['Title'], fontName="DejaVu-Bold", fontSize=20, alignment=TA_CENTER, spaceAfter=20)
            subtitle_style = ParagraphStyle('SubtitleStyle', parent=styles['Normal'], fontName="DejaVu", alignment=TA_CENTER, fontSize=12, spaceAfter=20)
            day_title_style = ParagraphStyle('DayTitleStyle', parent=styles['Heading4'], fontName="DejaVu-Bold", fontSize=13, spaceAfter=6)
            content_style = ParagraphStyle('ContentStyle', parent=styles['Normal'], fontName="DejaVu", fontSize=11, spaceAfter=4, leading=16)

            story = []

            story.append(Paragraph(self.title, title_style))
            story.append(Paragraph(f"Oluşturulma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}", subtitle_style))
            story.append(Paragraph("📅 Günlük Plan", styles['Heading2']))
            story.append(Spacer(1, 12))

            calisma_plani = plan_data.get("calisma_plani", [])
            logger.debug(f"Plan verisi {len(calisma_plani)} öğe içeriyor.")

            for index, item in enumerate(calisma_plani):
                def clean_text(text):
                    return text.replace("’", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("…", "...")

                gun = item.get("gun", "")
                konu = clean_text(item.get("konu", ""))
                alt_konu = clean_text(item.get("alt_konu", ""))
                etkinlik = clean_text(item.get("etkinlik", ""))
                gorev = clean_text(item.get("gorev", ""))
                tarih = item.get("tarih", "")
                tekrar = "Evet" if item.get("tekrar") else "Hayır"
                soru_coz = "Evet" if item.get("soru_coz") else "Hayır"

                story.append(Paragraph(f"<b>Gün {gun}: {konu} > {alt_konu}</b>", day_title_style))
                story.append(Paragraph(f"• Etkinlik: {etkinlik}", content_style))
                story.append(Paragraph(f"• Görev: {gorev}", content_style))
                story.append(Paragraph(f"• Tarih: {tarih}", content_style))
                story.append(Paragraph(f"• Tekrar: {tekrar} | Soru Çözümü: {soru_coz}", content_style))
                story.append(Spacer(1, 10))

                if (index + 1) % 4 == 0:
                    story.append(PageBreak())

            doc.build(story)
            buffer.seek(0)
            logger.info("PDF başarıyla oluşturuldu.")
            return buffer

        except Exception as e:
            logger.exception(f"PDF oluşturma sırasında hata oluştu: {e}")
            raise

# Örnek kullanım
if __name__ == "__main__":
    example_plan = {
        "calisma_plani": [
            {
                "gun": 1,
                "konu": "Matematik",
                "alt_konu": "Fonksiyonlar",
                "etkinlik": "Fonksiyon tanımlama ve grafik çizme",
                "gorev": "Fonksiyon sorularını çöz",
                "tarih": "2025-08-05",
                "tekrar": True,
                "soru_coz": True
            },
            {
                "gun": 2,
                "konu": "Fizik",
                "alt_konu": "Kuvvet ve Hareket",
                "etkinlik": "Kuvvet çeşitleri ve Newton yasaları",
                "gorev": "Newton yasaları ile ilgili test çöz",
                "tarih": "2025-08-06",
                "tekrar": False,
                "soru_coz": True
            }
        ]
    }

    exporter = PDFExporter()
    try:
        pdf_buffer = exporter.export_plan_to_pdf(example_plan)
        with open("plan.pdf", "wb") as f:
            f.write(pdf_buffer.getbuffer())
        logger.info("PDF başarıyla dosyaya kaydedildi: plan.pdf")
    except Exception as e:
        logger.error(f"PDF oluşturma veya kaydetme işlemi başarısız oldu: {e}")
