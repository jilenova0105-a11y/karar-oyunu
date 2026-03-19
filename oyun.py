import streamlit as st
import chess
import chess.svg
import chess.engine
import shutil
import time  # Bekleme süresi (Delay) için eklendi

# --- GÜVENLİK VE YAPILANDIRMA ---
st.set_page_config(page_title="Karar Senin: Satranç Akademi", layout="wide")

STOCKFISH_PATH = shutil.which("stockfish") or "/usr/games/stockfish"

# Taş İsimleri Sözlüğü (Dinamik metinler için)
TAS_ISIMLERI = {
    chess.PAWN: "Piyon",
    chess.KNIGHT: "At",
    chess.BISHOP: "Fil",
    chess.ROOK: "Kale",
    chess.QUEEN: "Vezir",
    chess.KING: "Şah"
}

# --- FONKSİYONLAR ---
@st.cache_resource
def get_engine():
    try:
        return chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    except Exception as e:
        st.error(f"Satranç motoru başlatılamadı. packages.txt dosyasını kontrol et. Hata: {e}")
        return None

def get_piece_name(board, square):
    """Karedeki taşın Türkçe adını döndürür"""
    piece = board.piece_at(square)
    return TAS_ISIMLERI.get(piece.piece_type, "Taş") if piece else "Taş"

def generate_ai_comment(board_before, move, board_after):
    """Eğitmenin KENDİ hamlesini profesyonel bir dille açıklaması"""
    piece_name = get_piece_name(board_before, move.from_square)
    to_sq = chess.square_name(move.to_square)
    
    if board_after.is_checkmate():
        return f"Şah ve Mat! {piece_name} ile {to_sq} karesine gelerek kaçış yollarını tamamen kapattım. Güzel bir oyundu!"
    elif board_after.is_check():
        return f"Şah! {piece_name} taşımı {to_sq} karesine oynayarak seni savunmaya zorluyorum ve inisiyatifi (saldırı sırasını) elime alıyorum."
    elif board_before.is_capture(move):
        return f"{to_sq} karesindeki taşını alarak materyal dengesini kendi lehime çevirdim. Bu taş değişimi benim pozisyonumu rahatlattı."
    elif board_before.is_castling(move):
        return "Rok atarak Şahımı merkezdeki ateş hattından çıkardım ve Kalemi oyuna dahil ettim. Güvenlik her şeyden önce gelir."
    elif piece_name == "At":
        return f"Atımı {to_sq} karesine zıplatarak merkez karelerin kontrolünü artırdım. Atlar kapalı pozisyonlarda rakibin savunmasını delmek için harikadır."
    elif piece_name == "Fil":
        return f"Filimi {to_sq} çaprazına yerleştirdim. Bu uzun menzilli baskı sayesinde senin kritik karelere yapacağın olası hamleleri kısıtlıyorum."
    elif piece_name == "Kale":
        return f"Kalemi {to_sq} karesine getirerek dikey hattı (açık yolu) ele geçirdim. Kaleler açık hatlarda inanılmaz güçlüdür."
    else:
        return f"{piece_name} taşımı {to_sq} karesine geliştirerek pozisyonumu sağlamlaştırdım ve alan kontrolümü artırdım."

def get_instructor_advice(board, engine):
    """Eğitmenin OYUNCUYA (sana) bir sonraki hamle için profesyonel tavsiyesi"""
    if engine is None or board.is_game_over():
        return "Oyun bitti.", None

    info = engine.analyse(board, chess.engine.Limit(time=1.0))
    best_move = info.get("pv")[0]
    score = info["score"].white()
    
    piece_name = get_piece_name(board, best_move.from_square)
    to_sq = chess.square_name(best_move.to_square)

    # Motor analizine göre pozisyonun genel değerlendirmesi
    if score.is_mate(): 
        durum_analizi = f"Dikkatli ol, {score.mate()} hamle içinde mat senaryosu var! Taktiksel bitiriciliğini kullan."
    elif score.cp > 100: 
        durum_analizi = "Şu an konum olarak üstünsün. Baskıyı artırmanın tam zamanı."
    elif score.cp < -100: 
        durum_analizi = "Pozisyonun şu an baskı altında. Dikkatli bir savunma yapmalısın."
    else: 
        durum_analizi = "Konum şu an oldukça dengeli. Stratejik bir üstünlük kurmaya çalışıyoruz."

    # Nokta atışı taş tavsiyesi
    if board.is_capture(best_move):
        tavsiye = f"Benim analizime göre en güçlü hamle **{piece_name}** ile **{to_sq}** karesindeki taşı alman. Bu hamle rakibin saldırı gücünü kıracaktır."
    elif piece_name == "At":
        tavsiye = f"En iyi seçenek **Atını {to_sq}** karesine gelmen. Böylece çatal atma potansiyeli yaratır veya rakibin önemli karelerini bloke edersin."
    elif piece_name == "Fil":
        tavsiye = f"Tavsiyem **Filini {to_sq}** karesine oynaman. Bu çaprazdaki baskı, rakibin (benim) taş gelişimini ciddi şekilde yavaşlatacaktır."
    elif piece_name == "Piyon":
        tavsiye = f"Şu an **Piyonunu {to_sq}** karesine sürmelisin. Bu hamle sana ekstra alan kazandıracak ve rakip taşları geri püskürtecektir."
    else:
        tavsiye = f"Bu pozisyonda **{piece_name}** taşını **{to_sq}** karesine oynamanı öneririm. Taşını daha aktif bir kareye taşıyıp inisiyatif almalısın."
            
    return f"{durum_analizi} {tavsiye}", best_move

# --- HAFIZA YÖNETİMİ ---
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
    st.session_state.ai_last_move = None
    st.session_state.ai_last_comment = "Oyuna Beyaz olarak sen başlıyorsun. Başlangıçta e4 veya d4 piyonlarıyla merkezi kontrol altına almanı tavsiye ederim."

# --- ARAYÜZ TASARIMI ---
st.title("🧩 Karar Senin: Satranç Akademi")
st.divider()

engine = get_engine()
col1, col2 = st.columns([1.2, 1])

with col1:
    board_svg = chess.svg.board(
        board=st.session_state.board, 
        size=450, 
        colors={'square light': '#ffffff', 'square dark': '#696969'} 
    )
    st.image(board_svg, use_container_width=False)
    
    st.write("")
    with st.form("move_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns([3, 1])
        with f_col1:
            move_input = st.text_input("Hamleniz:", placeholder="Örn: e4, Nf3 veya cxd4", label_visibility="collapsed")
        with f_col2:
            submit_move = st.form_submit_button("Hamle Yap", use_container_width=True)

with col2:
    st.subheader("🤖 Eğitmen Paneli (Siyah)")
    with st.container(border=True):
        if st.session_state.ai_last_move:
            st.markdown(f"**Son Hamlem:** `{st.session_state.ai_last_move}`")
        st.info(st.session_state.ai_last_comment)
    
    st.write("") 
    
    st.subheader("💡 Sıra Sende (Tavsiyeler)")
    if engine and not st.session_state.board.is_game_over():
        if st.session_state.board.turn == chess.WHITE:
            advice, best_move = get_instructor_advice(st.session_state.board, engine)
            with st.container(border=True):
                st.success(f"**Eğitmenin Analizi:** {advice}")
                st.markdown(f"**Hedef Hamle:** `{st.session_state.board.san(best_move)}`")
    
    if st.session_state.board.is_game_over():
        result = st.session_state.board.result()
        if result == "1-0": st.success("🏆 Mükemmel! Beni mat ettin. Satranç vizyonun harika.")
        elif result == "0-1": st.error("💥 Şah Mat! Bugün kaybettin ama hatalarından çok şey öğrendin. Tekrar deneyelim!")
        else: st.warning("🤝 Berabere. Taktiksel olarak ikimiz de birbirimize üstünlük kuramadık.")

    st.divider()
    
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
            
            # Oyuncunun hamlesini yap
            board_before_ai = board.copy()
            board.push(move)
            
            if not board.is_game_over():
                # EĞİTMENİN DÜŞÜNME SÜRESİ (2.5 Saniye Bekleme)
                with st.spinner('Eğitmen tahtayı inceliyor ve stratejisini kuruyor...'):
                    time.sleep(2.5) # Bu satır gecikme yaratır (Daha insani bir his)
                    
                    # Motor 1 saniye düşünerek hamleyi bulur
                    result = engine.play(board, chess.engine.Limit(time=1.0))
                    ai_move_san = board.san(result.move)
                    
                    # Dinamik Yorum Üretimi
                    ai_comment = generate_ai_comment(board, result.move, board.copy())
                    
                    st.session_state.ai_last_move = ai_move_san
                    st.session_state.ai_last_comment = ai_comment
                    
                    board.push(result.move)
            st.rerun()
        else:
            st.error("Bu hamle kurallara aykırı. Taşların önü kapalı olabilir veya Şahın tehdit altında.")
    except ValueError:
        st.error("Format anlaşılamadı. 'e4', 'Nf3' veya Piyon yemek için 'exd4' şeklinde girin.")
