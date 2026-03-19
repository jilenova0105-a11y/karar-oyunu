import streamlit as st
import random

# --- OYUN AYARLARI VE KELİME HAVUZU ---
st.set_page_config(page_title="Kelime Dehası", layout="centered")

# Sistem bu kelimelerden birini rastgele seçecek (İstersen burayı yüzlerce kelimeyle doldurabilirsin)
KELIMELER = ["GİRİŞ", "KREDİ", "YATIR", "HEDEF", "PROJE", "FİKİR", "START", "BİLİM", "ZEKAL", "OYUNC", "BEYİN"]

# --- OYUN MOTORU (HAFIZA) ---
def oyunu_baslat():
    if 'hedef_kelime' not in st.session_state:
        st.session_state.hedef_kelime = random.choice(KELIMELER)
        st.session_state.tahminler = [] # Oyuncunun önceki tahminlerini tutar
        st.session_state.oyun_bitti = False

def tahmini_kontrol_et(tahmin, hedef):
    sonuc = []
    hedef_harfler = list(hedef)
    
    # 1. Aşama: Doğru yerdeki harfleri (Yeşil) bul
    for i in range(5):
        if tahmin[i] == hedef[i]:
            sonuc.append({"harf": tahmin[i], "renk": "🟩"})
            hedef_harfler[i] = None # Bulunan harfi işaretle ki sarı kontrolde tekrar sayılmasın
        else:
            sonuc.append({"harf": tahmin[i], "renk": "⬜"}) # Şimdilik gri ata
            
    # 2. Aşama: Yanlış yerdeki harfleri (Sarı) bul
    for i in range(5):
        if sonuc[i]["renk"] == "⬜" and tahmin[i] in hedef_harfler:
            sonuc[i]["renk"] = "🟨"
            hedef_harfler[hedef_harfler.index(tahmin[i])] = None # Kullanılan harfi işaretle
            
    return sonuc

# --- ARAYÜZ ---
oyunu_baslat()

st.title("🧩 Kelime Dehası")
st.markdown("5 harfli gizli kelimeyi bulmak için **6 hakkın** var!")
st.caption("🟩: Doğru harf, doğru yer | 🟨: Doğru harf, yanlış yer | ⬜: Kelimede yok")
st.divider()

# Önceki tahminleri ekrana şık bir şekilde çizdir
for tahmin_dizisi in st.session_state.tahminler:
    satir = ""
    for kutu in tahmin_dizisi:
        satir += f"{kutu['renk']} **{kutu['harf']}** &nbsp;&nbsp;&nbsp;"
    st.markdown(f"### {satir}")

st.write("") # Boşluk

# Oyun bitmediyse tahmin formunu göster
if not st.session_state.oyun_bitti:
    with st.form("tahmin_formu", clear_on_submit=True):
        yeni_tahmin = st.text_input("5 Harfli Bir Kelime Girin:", max_chars=5).upper()
        gonder = st.form_submit_button("Tahmin Et")
        
        if gonder:
            if len(yeni_tahmin) != 5:
                st.error("Lütfen tam 5 harfli bir kelime girin!")
            elif not yeni_tahmin.isalpha():
                st.error("Sadece harf kullanmalısınız!")
            else:
                # Tahmini değerlendir ve hafızaya ekle
                degerlendirme = tahmini_kontrol_et(yeni_tahmin, st.session_state.hedef_kelime)
                st.session_state.tahminler.append(degerlendirme)
                
                # Kazanma veya Kaybetme Durumu
                if yeni_tahmin == st.session_state.hedef_kelime:
                    st.success("Tebrikler! Kelimeyi tam isabetle buldun. 🎉")
                    st.session_state.oyun_bitti = True
                elif len(st.session_state.tahminler) >= 6:
                    st.error(f"Maalesef hakların bitti! Gizli kelime: {st.session_state.hedef_kelime}")
                    st.session_state.oyun_bitti = True
                st.rerun()

# Oyun bittiyse "Yeniden Oyna" butonu çıkar
if st.session_state.oyun_bitti:
    st.divider()
    if st.button("🔄 Yeniden Oyna", type="primary", use_container_width=True):
        # Hafızayı sıfırla ve sayfayı yenile
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
