# Pro PDF Birleştirici 📄🔗

Python ve CustomTkinter kullanılarak geliştirilmiş; modern arayüze sahip, hızlı ve gelişmiş bir PDF birleştirme aracıdır. Standart birleştirme işlemlerinin yanı sıra sayfa aralığı seçme, PDF sıkıştırma ve şifreleme gibi profesyonel özellikler sunar.

## ✨ Özellikler

- **Modern Kullanıcı Arayüzü:** CustomTkinter ile tasarlanmış, işletim sistemi temasına (Aydınlık/Karanlık) duyarlı şık tasarım.
- **Esnek Dosya Yönetimi:** Tekli dosya veya klasör içindeki tüm PDF'leri topluca ekleyebilme.
- **Dinamik Sıralama:** Listeye eklenen dosyaları "Yukarı/Aşağı Taşı" butonları ile istenilen birleştirme sırasına koyma.
- **Sayfa Aralığı Belirleme:** Bir dosyanın tamamını değil, sadece belirli sayfalarını (Örn: `1-3, 5, 8-12`) birleştirmeye dahil edebilme.
- **Akıllı Sıkıştırma (PyMuPDF):** Birleştirilen devasa dosyaları kaliteden ödün vermeden 3 farklı seviyede (Hafif, Orta, Yüksek) sıkıştırabilme.
- **Güvenlik (Şifreleme):** Çıktı dosyasına parola koruması ekleyebilme.
- **Araya Boş Sayfa Ekleme:** Birleştirilen farklı belgelerin arasına otomatik olarak boş sayfa (ayırıcı) yerleştirme.
- **Asenkron İşlem:** Threading altyapısı sayesinde büyük dosyalar işlenirken arayüz donmaz ve işlem yüzdesi Progress Bar ile takip edilebilir.

## 🛠️ Gereksinimler

Projenin çalışması için bilgisayarınızda Python 3.x yüklü olmalıdır. Kullanılan ana kütüphaneler şunlardır:
- `customtkinter` (Modern Arayüz)
- `pypdf` (Sayfa okuma, birleştirme ve şifreleme)
- `PyMuPDF` (Dosya sıkıştırma ve RAM üzeri PDF manipülasyonu)

## 🚀 Kurulum ve Çalıştırma

1. Proje dosyalarını bilgisayarınıza indirin.
2. Terminal veya Komut İstemini (CMD) açarak proje dizinine gidin.
3. Gerekli kütüphaneleri yüklemek için aşağıdaki komutu çalıştırın:
   ```bash
   pip install -r requirements.txt