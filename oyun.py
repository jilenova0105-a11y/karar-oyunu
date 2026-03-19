import streamlit as st

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Karar Senin: Sistem Çöküşü", layout="centered")

# --- HİKAYE AĞACI (SÖZLÜK YAPISI) ---
# Burası oyunun beyni. Her 'durum' bir sahneyi ve o sahnedeki seçenekleri temsil eder.
hikaye = {
    "baslangic": {
        "metin": "Gece yarısı. Yüksek güvenlikli sunucu odasının önündesin. İçeriden kırmızı alarm ışıkları yanıp sönüyor. Çevresel sensörler bir anomali tespit etmiş ve ana kapı kilitlenmiş. Ne yapacaksın?",
        "secenekler": {
            "Tabletten sensör verilerini kontrol et": "sensor_kontrol",
            "Ana kapının şifre paneline müdahale et": "kapi_hack"
        }
    },
    "sensor_kontrol": {
        "metin": "Tableti açtın. Sunucu odasındaki sıcaklık hızla artıyor! Soğutma sistemi devreden çıkmış. Eğer müdahale etmezsen tüm donanım eriyecek.",
        "secenekler": {
            "Yedek soğutma sistemini uzaktan başlat": "yedek_sogutma",
            "Tüm sistemin gücünü keserek yangını önle": "guc_kes"
        }
    },
    "kapi_hack": {
        "metin": "Şifre paneline bağlandın ancak güvenlik duvarı çok güçlü. Yanlış bir deneme yaparsan sistem kendini tamamen kilitleyecek.",
        "secenekler": {
            "Risk al ve güvenlik duvarını kırmaya çalış": "duvar_kir",
            "Vazgeç ve sensör verilerini kontrol et": "sensor_kontrol"
        }
    },
    "yedek_sogutma": {
        "metin": "Tebrikler! Yedek soğutma devreye girdi. Sıcaklık düşüyor ve sunucular kurtarıldı. Kriz başarıyla yönetildi. 🏆",
        "secenekler": {"Yeniden Başla": "baslangic"}
    },
    "guc_kes": {
        "metin": "Tüm gücü kestin. Yangın önlendi ancak sunucular aniden kapandığı için kritik veri kayıpları yaşandı. Şirket büyük bir zararda... 💥",
        "secenekler": {"Yeniden Başla": "baslangic"}
    },
    "duvar_kir": {
        "metin": "Şifreyi kırmaya çalıştın ama sistem seni bir tehdit olarak algıladı ve tüm binayı kilitledi. Artık sen de içeride mahsur kaldın. Sistem çöktü. 🚨",
        "secenekler": {"Yeniden Başla": "baslangic"}
    }
}

# --- HAFIZA (SESSION STATE) ---
# Oyuncunun hangi sahnede olduğunu aklımızda tutuyoruz. İlk açılışta 'baslangic' noktasında olur.
if 'mevcut_durum' not in st.session_state:
    st.session_state.mevcut_durum = "baslangic"

# --- ARAYÜZ ---
st.title("🖥️ Karar Senin: Sistem Çöküşü")
st.divider()

# Mevcut durumu (sahneyi) değişkene al
durum = st.session_state.mevcut_durum
mevcut_sahne = hikaye[durum]

# 1. Hikaye metnini ekrana yazdır
st.markdown(f"### {mevcut_sahne['metin']}")
st.write("")
st.write("")

# 2. O sahnedeki seçenekleri buton olarak ekrana diz
for secenek_metni, hedef_durum in mevcut_sahne['secenekler'].items():
    # Butona basıldığında hafızadaki durumu hedef durumla değiştir ve sayfayı yenile
    if st.button(secenek_metni, use_container_width=True):
        st.session_state.mevcut_durum = hedef_durum
        st.rerun()

st.divider()
st.caption("Geliştirici: Yusuf | Dürüst Kredi Rehberi'nden sonraki yeni macera!")
