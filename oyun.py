import streamlit as st
import chess
import chess.svg
import chess.engine
import shutil

# --- GÜVENLİK VE YAPILANDIRMA ---
st.set_page_config(page_title="Karar Senin: Satranç Akademi", layout="wide")

STOCKFISH_PATH = shutil.which("stockfish") or "/usr/games/stockfish"

# Eğitmenin oyuncuya vereceği dersler
EGITMEN_DERSLERI = {
    "acilis_merkez": "Harika bir karar! Satrançta ilk kural merkezi (e4, d4, e5, d5) kontrol etmektir.",
    "gelisim_ati": "Atları erken oyunda geliştirmek çok güçlü bir stratejidir. Merkezi tehdit ediyorsun.",
    "gelisim_fil": "Filini geliştirdin, şimdi rok atmaya (şahı güvenliğe almaya) bir adım daha yaklaştın.",
    "rok": "Mükemmel! Şahını güvenli bir kaleye aldın ve kaleni oyuna soktun. Savunmanın temeli budur.",
    "atak_firsati": "Rakip pozisyonunda zayıflık var! Şimdi taktik bir atak yapabiliriz. İyi analiz et.",
    "savunma_gerekli": "Rakibin şahına yaklaşıyor. Saldırıyı bırakıp savunmaya odaklanmalısın. Şah güvenliği esastır.",
    "dengeli": "Konum dengeli. Rakibinin zayıf bir noktasını bulmaya çalış ve taşlarını daha aktif karelere getir."
}

# --- FONKSİYONLAR ---
@st.cache_resource
def get_engine():
    try:
        return chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    except Exception as e:
        st.error(f"Satranç motoru başlatılamadı. packages.txt dosyasının olduğundan emin ol. Hata: {e}")
        return None

def generate_ai_comment(board, move):
    """Eğitmenin yaptığı kendi hamlesini mantıksal olarak açıklaması"""
    if board.is_capture(move):
        return "Taş avantajı sağlamak veya tehdidi ortadan kaldırmak için taş değişimi yapıyorum."
    elif board.is_castling(move):
        return "Savunmamı güçlendirmek için şahımı güvenli bölgeye (rok) alıyorum."
    elif move.promotion:
        return "Piyonumu terfi ettirerek gücüme güç katıyorum!"
    else:
        return "Konumumu iyileştirmek, alan kontrolünü sağlamak ve taşımı geliştirmek için bu hamleyi tercih ettim."

def get_instructor_advice(board, engine):
    """Eğitmenin oyuncuya sıradaki hamlesi için tavsiyesi"""
    if engine is None or board.is_game_over():
        return "Oyun bitti.", None

    info = engine.analyse(board, chess.engine.Limit(time=0.5))
    best_move = info.get("pv")[0]
    score = info["score"].white()

    advice = ""
    move_uci = best_move.uci()
    if board.fullmove_number <= 5:
        if move_uci in ["e2e4", "d2d4"]: advice = EGITMEN_DERSLERI["acilis_merkez"]
        elif move_uci in ["g1f3", "b1c3"]: advice = EGITMEN_DERSLERI["gelisim_ati"]
        elif move_uci in ["f1c4", "e1g1"]: advice = EGITMEN_DERSLERI["rok"]
        else: advice = "Taşlarını geliştirmeye ve merkezi kontrol etmeye odaklan."
    else:
        if score.is_mate(): advice = f"Dikkat! {score.mate()} hamlede mat var! Çok iyi analiz et."
        elif score.cp > 100: advice = f"{EGITMEN_DERSLERI['atak_firsati']} Konumumuz çok iyi (+{score.cp/100:.1f})."
        elif score.cp < -100: advice = f"{EGITMEN_DERSLERI['savunma_gerekli']} Konumumuz kötü ({score.cp/100:.1f})."
        else: advice = EGITMEN_DERSLERI["dengeli"]
            
    return advice, best_move

# --- HAFIZA YÖNETİMİ ---
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
    st.session_state.ai_last_move = None
    st.session_state.ai_last_comment = "Oyuna Beyaz olarak sen başlıyorsun. Başlangıçta merkez (e4, d4) kontrolüne dikkat etmeni öneririm."

# --- ARAYÜZ TASARIMI ---
st.title("🧩 Karar Senin: Satranç Akademi")
st.divider()

engine = get_engine()

# Mobil uyumlu 2 sütunlu düzen
col1, col2 = st.columns([1.2, 1])

with col1:
    # 1. İstek: Siyah-Beyaz (Gri-Beyaz) Zeminli 2D Görünüm
    board_svg = chess.svg.board(
        board=st.session_state.board, 
        size=450, 
        colors={'square light': '#ffffff', 'square dark': '#696969'} 
    )
    st.image(board_svg, use_container_width=False)
    
    st.write("")
    # 3. İstek: Küçültülmüş Hamle Butonu
    with st.form("move_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns([3, 1])
        with f_col1:
            move_input = st.text_input("Hamleniz:", placeholder="Örn: e4 veya Nf3", label_visibility="collapsed")
        with f_col2:
            submit_move = st.form_submit_button("Hamle Yap", use_container_width=True)

with col2:
    # 5 & 6. İstek: Eğitmen kendi hamlesi (Yukarıda)
    st.subheader("🤖 Eğitmen Paneli (Siyah)")
    with st.container(border=True):
        if st.session_state.ai_last_move:
            st.markdown(f"**Son Hamlem:** `{st.session_state.ai_last_move}`")
        st.info(st.session_state.ai_last_comment)
    
    st.write("") 
    
    # 5 & 6. İstek: Oyuncu tavsiyesi (Aşağıda)
    st.subheader("💡 Sıra Sende (Tavsiyeler)")
    if engine and not st.session_state.board.is_game_over():
        if st.session_state.board.turn == chess.WHITE:
            advice, best_move = get_instructor_advice(st.session_state.board, engine)
            with st.container(border=True):
                st.success(f"**Analizim:** {advice}")
                st.markdown(f"**Önerdiğim Hamle:** `{st.session_state.board.san(best_move)}`")
    
    # Oyun Bitiş Kontrolü
    if st.session_state.board.is_game_over():
        result = st.session_state.board.result()
        if result == "1-0": st.success("🏆 Tebrikler! Harika bir analiz yeteneği sergiledin ve beni yendin.")
        elif result == "0-1": st.error("💥 Kaybettin. Rakibin hamlelerini tahmin etme konusunda pratik yapmaya devam!")
        else: st.warning("🤝 Berabere. İki taraf da iyi direndi.")

    st.divider()
    
    # 4. İstek: Küçültülmüş Yeni Oyun Butonu
    btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
    with btn_col2:
        if st.button("🔄 Yeni Oyun", use_container_width=True):
            st.session_state.board.reset()
            st.session_state.ai_last_move = None
            st.session_state.ai_last_comment = "Yeni oyun! Beyaz olarak sen başlıyorsun. Merkez kontrolüne dikkat et."
            st.rerun()

# --- HAMLE İŞLEME ---
if submit_move and move_input:
    board = st.session_state.board
    try:
        move = board.parse_san(move_input) if move_input[0].isupper() else board.parse_uci(move_input)
        if move in board.legal_moves:
            board.push(move)
            
            if not board.is_game_over():
                with st.spinner('Eğitmen analiz yapıyor...'):
                    result = engine.play(board, chess.engine.Limit(time=1.0))
                    ai_move_san = board.san(result.move)
                    
                    # Yapay zeka kendi hamlesini açıklar
                    ai_comment = generate_ai_comment(board, result.move)
                    
                    st.session_state.ai_last_move = ai_move_san
                    st.session_state.ai_last_comment = ai_comment
                    
                    board.push(result.move)
            st.rerun()
        else:
            st.error("Bu hamle kurallara aykırı veya imkansız. Lütfen tekrar analiz edin.")
    except ValueError:
        st.error("Format anlaşılamadı. Lütfen 'e4', 'Nf3' veya 'e2e4' şeklinde girin.")
