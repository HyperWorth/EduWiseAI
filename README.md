# 🎓 EduWiseAI
````markdown
## ✨ Kısa Açıklama

**EduWiseAI**, yapay zekâ destekli bir eğitim asistanıdır.  
Bu uygulama, öğrencilerin ve eğitimcilerin öğrenme süreçlerini kolaylaştırmak için geliştirilmiştir. Kullanıcılar; konu haritaları oluşturabilir, günlük kişiselleştirilmiş çalışma planları hazırlayabilir ve seçtikleri konulara özel pratik sorular üretebilir.

BTK Hackathon kapsamında geliştirilen bu proje, LLM (Large Language Model) teknolojisinin eğitime entegrasyonu üzerine odaklanmaktadır.

---

## 🛠 Kullanılan Teknolojiler

- **Python 3.12+**
- **[Streamlit](https://streamlit.io/)** – Web arayüzü için
- **[Google Generative AI (Gemini)](https://ai.google.dev/)** – LLM tabanlı içerik üretimi
- `python-dotenv` – Ortam değişkenlerini yönetmek için
- `requests` – API istekleri
- Özel `logger.py` – Hata ayıklama ve loglama

---

## ⚙️ Kurulum Adımları

> Projeyi çalıştırmadan önce `Python 3.12+` sürümüne sahip olmanız önerilir.

```bash
# 1. Depoyu klonlayın veya zip dosyasını çıkarın
git clone https://github.com/HyperWorth/EduWiseAI.git
cd EduWiseAI

# 2. Sanal ortam oluşturun (isteğe bağlı fakat önerilir)
python -m venv venv
source venv/bin/activate  # Windows için: venv\Scripts\activate

# 3. Gerekli bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Ortam değişkenlerini ayarlayın
# .env dosyası içinde aşağıdaki gibi bir API anahtarı tanımlayın:
GOOGLE_API_KEY=your_gemini_api_key_here
````

---

## ▶️ Nasıl Kullanılır?

```bash
streamlit run app.py
```

Ardından tarayıcınızda otomatik olarak açılacaktır. (Varsayılan olarak `http://localhost:8501`)

### Uygulama İçinde Neler Yapabilirsiniz?

1. **Konu girin:** Örneğin "Fotosentez" yazın.
2. **Bir araç seçin:**

   * Konu Haritası Oluştur
   * Çalışma Planı Oluştur
   * Soru Üret
3. **"Gönder" butonuna tıklayın:** Yapay zekâ, seçtiğiniz araca göre size içerik üretsin.
4. **İçeriği kopyalayın veya başka bir araçla devam edin.**

---

## 🎥 Demo

📽 [Demo Videosunu İzle](demo-linki-buraya)

> Video yayına alındığında buradaki bağlantı güncellenmelidir.

---

## 🤝 Katkıda Bulunma

Katkılarınızı memnuniyetle karşılıyoruz!
Lütfen aşağıdaki adımları takip edin:

1. Fork’layın 🍴
2. Yeni bir dal (branch) oluşturun: `git checkout -b feature/yenilik`
3. Değişiklikleri yapın ve commit edin: `git commit -m 'Yeni özellik eklendi'`
4. Dalınızı push’layın: `git push origin feature/yenilik`
5. Pull Request gönderin ✅

---

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.

---

> Geliştirici: Muhammed Ali UĞUR

```

