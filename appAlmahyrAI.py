import streamlit as st
import google.generativeai as genai
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Almahyr AI", page_icon="✨", layout="centered")

# --- CSS KUSTOM ---
st.markdown("""
<style>
    .stApp { background-color: #F0F8FF; }
    h1 { color: #2E8B57; font-family: 'Comic Sans MS', cursive, sans-serif; text-align: center; text-shadow: 2px 2px #E0FFFF; }
    .login-box { background-color: white; padding: 30px; border-radius: 20px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); border-top: 5px solid #2E8B57; }
    .stButton>button { border-radius: 20px; background-color: #FF7F50; color: white; font-weight: bold; border: none; transition: all 0.3s; }
    .stButton>button:hover { background-color: #FF6347; transform: scale(1.05); }
</style>
""", unsafe_allow_html=True)

# --- INISIALISASI SESSION STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = ""
if "api_key" not in st.session_state: st.session_state.api_key = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "chat_session" not in st.session_state: st.session_state.chat_session = None

modes = {
    "1": "Latihan Mendengarkan (Istima')",
    "2": "Bermain Peran (Role Play / Kalam)",
    "3": "Kuis Seru Al-Mihnah"
}

# --- HALAMAN LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<h1>✨ Almahyr AI ✨</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #555;'>Teman Belajar Bahasa Arab Kelas 4 MI</h4>", unsafe_allow_html=True)
    
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    user_input = st.text_input("Masukkan Namamu (Username):", placeholder="Contoh: Ahmad")
    api_key_input = st.text_input("Masukkan API Key Google AI Studio:", type="password")
    
    if st.button("Mulai Belajar! 🚀", use_container_width=True):
        if user_input and api_key_input:
            st.session_state.username = user_input
            st.session_state.api_key = api_key_input
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.warning("Nama dan API Key tidak boleh kosong, ya!")
    st.markdown("</div>", unsafe_allow_html=True)

# --- HALAMAN UTAMA (CHAT) ---
else:
    # Fungsi pencari model otomatis
    @st.cache_data(show_spinner=False)
    def dapatkan_model_valid(api_key):
        try:
            genai.configure(api_key=api_key)
            daftar_model = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # Cari model flash 1.5 terlebih dahulu
            for m in daftar_model:
                if 'gemini-1.5-flash' in m:
                    return m
            # Jika tidak ada, ambil model pertama yang tersedia
            if daftar_model:
                return daftar_model[0]
            return None
        except Exception:
            return None

    with st.sidebar:
        st.markdown(f"### Ahlan wa Sahlan, **{st.session_state.username}**! 🌟")
        st.divider()
        guru = st.radio("Pilih Pendamping Belajarmu:", ["Ustadz Rafli 👨‍🏫", "Ustadzah Fatimah 👩‍🏫"])
        mode_pilihan = st.selectbox("Pilih Mode Pembelajaran:", list(modes.values()))
        st.divider()
        if st.button("Keluar / Ganti Akun 🚪"):
            st.session_state.clear()
            st.cache_data.clear()
            st.rerun()

    st.markdown("<h1>Almahyr AI</h1>", unsafe_allow_html=True)
    st.markdown(f"<h5 style='text-align: center;'>Bersama {guru} | Topik: Al-Mihnah (Profesi)</h5>", unsafe_allow_html=True)

    current_setting = f"{guru}-{mode_pilihan}"
    if "last_setting" not in st.session_state or st.session_state.last_setting != current_setting:
        st.session_state.messages = []
        st.session_state.last_setting = current_setting
        
        persona = "Ustadz Rafli yang sabar, ceria, dan suka memberi semangat" if "Rafli" in guru else "Ustadzah Fatimah yang lembut, ceria, dan sangat interaktif"
        
        instruksi_rahasia = f"""
        Mulai sekarang, kamu adalah {persona}. Kamu sedang mengajar bahasa Arab untuk anak kelas 4 Madrasah Ibtidaiyah (MI).
        Lawan bicaramu adalah murid bernama {st.session_state.username}. Topik pembelajaran: 'Al-Mihnah' (Profesi).
        Aturan: Gunakan bahasa Indonesia yang ramah, selipkan kosakata Arab profesi. Jangan beri jawaban panjang.
        Mode: {mode_pilihan}. Ajak interaksi. Jawab "SAYA MENGERTI" jika siap mematuhi ini.
        """
        
        # Mengecek model yang tersedia secara otomatis
        model_name = dapatkan_model_valid(st.session_state.api_key)
        
        if model_name:
            try:
                model = genai.GenerativeModel(model_name)
                # Menyuntikkan instruksi ke dalam riwayat obrolan secara manual
                riwayat_awal = [
                    {"role": "user", "parts": [instruksi_rahasia]},
                    {"role": "model", "parts": ["SAYA MENGERTI"]}
                ]
                
                st.session_state.chat_session = model.start_chat(history=riwayat_awal)
                
                sapaan_awal = f"Assalamu'alaikum, {st.session_state.username}! Ahlan wa sahlan di Almahyr AI. Saya {guru.split()[0]} {guru.split()[1]} yang akan menemani kamu belajar tentang profesi (Al-Mihnah). Apakah kamu sudah siap?"
                st.session_state.messages.append({"role": "model", "content": sapaan_awal})
                
            except Exception as e:
                st.error(f"Terjadi kesalahan saat menyiapkan obrolan. Detail: {e}")
        else:
            st.error("🚨 API Key kamu tidak valid atau tidak diizinkan mengakses model. Silakan buat API Key baru di Google AI Studio.")

    # Menampilkan percakapan
    for message in st.session_state.messages:
        avatar = "🧑‍🎓" if message["role"] == "user" else "🕌"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # Input pengguna
    if prompt := st.chat_input("Tulis pesan atau jawabanmu di sini..."):
        if prompt.lower() in ['exit', 'quit', 'keluar']:
            st.toast("Terima kasih sudah belajar di Almahyr AI! Sampai jumpa lagi.")
            time.sleep(2)
            st.session_state.clear()
            st.cache_data.clear()
            st.rerun()

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍🎓"):
            st.markdown(prompt)

        with st.chat_message("model", avatar="🕌"):
            message_placeholder = st.empty()
            try:
                if st.session_state.chat_session:
                    response = st.session_state.chat_session.send_message(prompt)
                    message_placeholder.markdown(response.text)
                    st.session_state.messages.append({"role": "model", "content": response.text})
            except Exception as e:
                message_placeholder.error(f"Koneksi terputus atau respon ditolak oleh API. Coba kirim ulang. Detail: {e}")