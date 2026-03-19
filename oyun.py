import streamlit as st
import chess
import chess.svg
import chess.engine
import shutil

# --- GÜVENLİK VE YAPILANDIRMA ---
st.set_page_config(page_title="Karar Senin: Satranç Akademi", layout="wide")

# Sistemden Stockfish'i bul (Artık GitHub'a 35 MB dosya yüklemeye gerek yok!)
STOCKFISH_PATH = shutil.which("stockfish") or "/usr/games/stockfish"

# Pedagojik Veritabanı (Eğitmenin vereceği dersler)
EGITMEN_DERSLERI = {
    "acilis_merkez": "Harika bir karar! Satrançta ilk kural merkezi (e4, d4, e5, d5) kontrol etmektir.",
    "gelisim_ati": "Atları erken oyunda geliştirmek çok güçlü bir stratejidir. Merkezi tehdit ediyorsun.",
    "gelisim_fil": "Filini geliştirdin, şimdi rok atmaya (şahı güvenliğe almaya) bir adım daha yaklaştın.",
    "rok": "Mükemmel! Şahını güvenli bir kaleye aldın ve kaleni oyuna soktun. Savunmanın temeli budur.",
    "atak_firsati": "Rakip pozisyonunda zayıflık var! Şimdi taktik bir atak yapabiliriz. İyi analiz et.",
    "savunma_gerekli": "Rakibin şahına yaklaşıyor. Saldırıyı bırakıp savunmaya odaklanmalısın. Şah güvenliği esastır."
}

# --- FONKSİYONLAR ---
@st.cache_resource
def get_engine():
    try:
        return chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    except Exception as e:
        st.error(f"Satranç motoru başlatılamadı. packages.txt dosyasının olduğundan emin ol. Hata: {e}")
        return None

def get_instructor_advice(board, engine):
    if engine is None or board.is_game_over():
        return "Oyun bitti veya motor hazır değil.", None

    info = engine.analyse(board, chess.engine.Limit(time=0.5))
    best_move = info.get("pv")[0]
    score = info["score"].white()

    advice = ""
    if board.turn == chess.WHITE: 
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
            else: advice = "Konum dengeli. Rakibinin zayıf bir noktasını bulmaya çalış."
            
    return advice, best_move

# --- HAFIZA YÖNETİMİ ---
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
    st.session_state.history = []

# --- ARAYÜZ TASARIMI ---
st.title("🧩 Karar Senin: Satranç Akademi")
st.divider()

engine = get_engine()
col1, col2 = st.columns([2, 1])

with col1:
    board_svg = chess.svg.board(board=st.session_state.board, size=550)
    st.image(board_svg, use_container_width=False)
    
    st.write("")
    with st.form("move_form", clear_on_submit=True):
        move_input = st.text_input("Hamlenizi girin (Örn: e2e4 veya Nf3):")
        submit_move = st.form_submit_button("Hamle Yap", type="primary")

with col2:
    st.subheader("👨‍🏫 Eğitmen Paneli")
    
    if engine and not st.session_state.board.is_game_over():
        if st.session_state.board.turn == chess.WHITE:
            advice, best_move = get_instructor_advice(st.session_state.board, engine)
            with st.container(border=True):
                st.info(advice)
                st.markdown(f"**Eğitmen Önerisi:** `{st.session_state.board.san(best_move)}`")
                st.caption("Bu hamle stratejik bir avantaj elde etmeni sağlar. Karar senin!")

        if st.session_state.board.is_game_over():
            result = st.session_state.board.result()
            if result == "1-0": st.success("🏆 Tebrikler! Harika bir analiz yeteneği sergiledin.")
            elif result == "0-1": st.error("💥 Kaybettin. Rakibin hamlelerini tahmin etme konusunda çalışmalıyız.")
            else: st.warning("🤝 Berabere. İki taraf da iyi analiz etti.")

    st.divider()
    st.write("**Oyun Geçmişi:**")
    st.write(", ".join(st.session_state.history))
    if st.button("🔄 Yeni Oyun", use_container_width=True):
        st.session_state.board.reset()
        st.session_state.history = []
        st.rerun()

# --- HAMLE İŞLEME ---
if submit_move and move_input:
    board = st.session_state.board
    try:
        move = board.parse_san(move_input) if move_input[0].isupper() else board.parse_uci(move_input)
        if move in board.legal_moves:
            st.session_state.history.append(board.san(move))
            board.push(move)
            
            if not board.is_game_over():
                with st.spinner('Rakip (Eğitmen) analiz yapıyor...'):
                    result = engine.play(board, chess.engine.Limit(time=1.0))
                    st.session_state.history.append(board.san(result.move))
                    board.push(result.move)
            st.rerun()
        else:
            st.error("Bu hamle kurallara aykırı. Lütfen tekrar analiz edin.")
    except ValueError:
        st.error("Hamle formatı anlaşılamadı. Lütfen 'e2e4' veya 'Nf3' gibi girin.")
