import streamlit as st
import pdfplumber
import re
from gtts import gTTS
import io
from deep_translator import GoogleTranslator
# ---- [Custom Styling] ----
st.markdown("""
    <style>
    body {
        background-color: #f5f7fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #333;
    }
    .reportview-container {
        padding: 2rem 3rem;
        max-width: 900px;
        margin: auto;
    }
    h1 {
        color: #2c3e50;
        font-weight: 700;
        letter-spacing: 1.2px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: black;
        font-size: 16px;
        padding: 10px 25px;
        border: none;
        border-radius: 8px;
        transition: background-color 0.3s ease;
        cursor: pointer;
        width: 100%;
        max-width: 300px;
    }
    .stButton>button:hover {
        background-color: #45a049;
        color: white;
    }
    .stRadio > div {
        flex-direction: row;
        gap: 20px;
    }
   mark {
        background-color: #fffb91;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 600;
    }
    .stTextArea textarea {
        font-size: 16px;
        line-height: 1.6;
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        background-color: #fff;
        resize: vertical;
    }
    .stMarkdown, .stTextArea, .stButton {
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)



st.set_page_config(page_title="EqualDocs", layout="centered")

KEYWORDS = {
    "Date": {"en": "The date when the form is filled or signed.", "ur": "یہ فارم بھرنے یا دستخط کرنے کی تاریخ ہے۔"},
    "Name": {"en": "Your full legal name.", "ur": "آپ کا مکمل قانونی نام۔"},
    "Signature": {"en": "Your official signature to confirm agreement.", "ur": "معاہدے کی تصدیق کے لیے آپ کے دستخط۔"},
    "Address": {"en": "Your current residential address.", "ur": "آپ کا موجودہ رہائشی پتہ۔"},
    "Phone": {"en": "Your contact phone number.", "ur": "آپ کا رابطہ فون نمبر۔"},
    "Email": {"en": "Your email address.", "ur": "آپ کا ای میل ایڈریس۔"},
    "DOB": {"en": "Date of Birth - your birth date.", "ur": "تاریخ پیدائش۔"},
    "Amount": {"en": "Monetary value or amount related to the form.", "ur": "رقم یا فارم سے متعلق مالی قیمت۔"}
}

def highlight_keywords(text, keywords):
    pattern = r'(' + '|'.join(re.escape(k) for k in keywords.keys()) + r')'
    return re.sub(pattern, r'<mark>\1</mark>', text, flags=re.IGNORECASE)

def get_summary(text, sentences=3):
    sent_list = re.split(r'(?<=[.!?]) +', text)
    return ' '.join(sent_list[:sentences])
# ---- [Styled Title] ----
st.markdown("""
    <h1 style='text-align: center; color: #4CAF50; margin-bottom: 0;'>
        📄 EqualDocs
    </h1>
    <p style='text-align: center; font-size: 18px; color: gray;'>
        Smart Form Assistant – Read, Explain & Speak PDF Forms
    </p>
""", unsafe_allow_html=True)


# Language toggle buttons
col1, col2 = st.columns(2)
with col1:
    en_clicked = st.button("🇬🇧 English", use_container_width=True)
with col2:
    ur_clicked = st.button("🇵🇰 اردو", use_container_width=True)

# Set default language
if "lang_code" not in st.session_state:
    st.session_state.lang_code = "en"

# Update based on button click
if en_clicked:
    st.session_state.lang_code = "en"
if ur_clicked:
    st.session_state.lang_code = "ur"

# Use the selected language in the rest of the app
lang_code = st.session_state.lang_code
language = "English" if lang_code == "en" else "Urdu"

lang_code = "en" if language == "English" else "ur"

uploaded_file = st.file_uploader("📤 Upload PDF File", type=["pdf"])

if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        full_text = "\n\n".join(page.extract_text() or "" for page in pdf.pages)

    if not full_text.strip():
        st.warning("⚠️ No text found in the uploaded file.")
    else:
        st.subheader("📝 " + {"en": "Extracted Text", "ur": "نکالا گیا متن"}[lang_code])
        st.text_area("📄", full_text, height=300)

        st.subheader("🔍 " + {"en": "Highlighted Keywords", "ur": "نمایاں کردہ الفاظ"}[lang_code])
        highlighted = highlight_keywords(full_text, KEYWORDS)
        st.markdown(highlighted, unsafe_allow_html=True)

        found_keywords = [k for k in KEYWORDS if re.search(k, full_text, re.IGNORECASE)]
        if found_keywords:
            st.subheader("📘 " + {"en": "Keyword Explanations", "ur": "الفاظ کی وضاحت"}[lang_code])
            for kw in found_keywords:
                st.markdown(f"**{kw}**: {KEYWORDS[kw][lang_code]}")

        summary = get_summary(full_text)
        translated_summary = (
            GoogleTranslator(source='auto', target='ur').translate(summary)
            if lang_code == 'ur' else summary
        )

        st.subheader("🧾 " + {"en": "Document Summary", "ur": "دستاویز کا خلاصہ"}[lang_code])
        st.write(translated_summary)

        try:
            st.subheader("🔊 " + {"en": "Listen to Summary", "ur": "خلاصہ سنیں"}[lang_code])
            tts = gTTS(text=translated_summary[:500], lang=lang_code)
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            st.audio(audio_fp, format='audio/mp3')
        except Exception as e:
            st.error("❌ Failed to generate audio.")
