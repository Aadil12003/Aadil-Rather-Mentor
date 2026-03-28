import warnings
warnings.filterwarnings("ignore")
import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import io
import re

st.set_page_config(
    page_title="Aadil Mentor", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── PREMIUM CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
}

.main-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
}

.main-header h1 {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #f7971e, #ffd200);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

.main-header p {
    color: #a0a0c0;
    font-size: 1.1rem;
}

.selector-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
}

.chat-container {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    min-height: 400px;
    margin-bottom: 1rem;
}

.explanation-box {
    background: linear-gradient(135deg, rgba(102,126,234,0.2), rgba(118,75,162,0.2));
    border-left: 4px solid #667eea;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
}

.exam-box {
    background: linear-gradient(135deg, rgba(34,193,195,0.15), rgba(253,187,45,0.15));
    border-left: 4px solid #22c1c3;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
}

.tip-box {
    background: rgba(255,200,0,0.1);
    border-left: 4px solid #ffd200;
    border-radius: 12px;
    padding: 0.8rem 1.2rem;
    margin: 0.8rem 0;
    font-size: 0.95rem;
}

.visual-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 12px;
    padding: 1.2rem;
    margin: 1rem 0;
    font-family: monospace;
}

.stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: white !important;
}

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: white !important;
}

.stButton > button {
    background: linear-gradient(90deg, #f7971e, #ffd200) !important;
    color: #1a1a2e !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.6rem 1.5rem !important;
    width: 100% !important;
}

.stDownloadButton > button {
    background: linear-gradient(90deg, #22c1c3, #6dd5ed) !important;
    color: #1a1a2e !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    width: 100% !important;
}

.stChatInput > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 12px !important;
}

.metric-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}

div[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 12px !important;
    margin-bottom: 0.8rem !important;
    padding: 0.8rem !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
}

label, .stSelectbox label {
    color: #a0a0c0 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
</style>
""", unsafe_allow_html=True)

# ─── HEADER ───
st.markdown("""
<div class="main-header">
    <h1>🎓 Aadil Mentor</h1>
    <p>Har student ka personal AI mentor — Hinglish mein samjho, English mein likho!</p>
</div>
""", unsafe_allow_html=True)

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=st.secrets["NVIDIA_API_KEY"]
)

SUBJECTS = [
    "Physics", "Chemistry", "Biology", "Mathematics",
    "Anatomy", "Physiology", "Pharmacology", "Pathology",
    "Microbiology", "Biochemistry", "Nursing Fundamentals",
    "Medical Surgical Nursing", "Pediatric Nursing",
    "Obstetric Nursing", "Community Health Nursing",
    "MBBS General Medicine", "Surgery", "Psychiatry",
    "JEE Mathematics", "JEE Physics", "JEE Chemistry",
    "NEET Biology", "NEET Physics", "NEET Chemistry",
    "UPSC History", "UPSC Geography", "UPSC Polity",
    "UPSC Economics", "UPSC Current Affairs",
    "History", "Geography", "Political Science",
    "Economics", "Sociology", "Psychology",
    "Philosophy", "English Literature", "Hindi Literature",
    "Art & Drawing", "Jewellery Design", "Fashion Design",
    "Graphic Design", "Interior Design",
    "Computer Science", "Programming Basics",
    "Artificial Intelligence", "Data Science",
    "General Knowledge", "Current Affairs", "English Grammar"
]

LEVELS = {
    "Class 10 aur neeche": {
        "words": "100-150 words",
        "style": "Very simple words. Short sentences. Basic examples only."
    },
    "Class 11-12 (Board Exams)": {
        "words": "200-300 words",
        "style": "Key points, definitions, examples. Board exam format."
    },
    "College/University": {
        "words": "400-500 words",
        "style": "In-depth with theory, examples, and analysis."
    },
    "Competitive Exams (JEE/NEET/UPSC)": {
        "words": "400-600 words",
        "style": "All key facts, formulas, diagrams, exam tips."
    }
}

def get_system_prompt(level, subject):
    info = LEVELS[level]
    return f"""You are Aadil Mentor — expert Indian study mentor for {level} students studying {subject}.

ALWAYS structure your response in EXACTLY this format with these exact headers:

🗣️ HINGLISH EXPLANATION:
[Explain in simple Hinglish. Use "dekho", "samjho", "basically". Use Indian examples. Make it conversational like a friend.]

📊 VISUAL OVERVIEW:
[Create a simple ASCII visual or structured diagram like:
- Flow charts using arrows →
- Tables using | symbols
- Numbered hierarchies
- Mind map style with branches
Make it clear and useful for understanding the topic visually.]

✅ EXAM READY ANSWER:
[Pure English only. {info['words']}. {info['style']} Proper structured answer with clear points. No Hindi.]

💡 EXAM TIP:
[One powerful tip in Hinglish for this topic in exam]

STRICT RULES:
- Never skip any section
- Visual Overview must always be present and useful
- Exam Ready Answer must always be in pure English
- Answer length must match level: {info['words']}
- Never sound like AI
- For QUIZ mode: give 5 MCQs first, then score, then full exam answer
- Always be encouraging"""

def generate_pdf(notes):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(247, 151, 30)
    pdf.cell(0, 15, "AADIL MENTOR - STUDY NOTES", ln=True, align="C")
    
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Your Personal AI Study Guide", ln=True, align="C")
    pdf.ln(5)
    
    pdf.set_draw_color(247, 151, 30)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)
    
    for i, note in enumerate(notes, 1):
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(247, 151, 30)
        pdf.cell(0, 10, f"NOTE {i}: {note['subject']}", ln=True)
        
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 6, f"Level: {note['level']}", ln=True)
        pdf.cell(0, 6, f"Question: {note['question']}", ln=True)
        pdf.ln(3)
        
        clean = note['answer'].encode('latin-1', 'replace').decode('latin-1')
        clean = re.sub(r'[^\x00-\x7F]+', ' ', clean)
        
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 6, clean)
        pdf.ln(5)
        
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(8)
    
    return bytes(pdf.output())

# ─── SESSION STATE ───
if "messages" not in st.session_state:
    st.session_state.messages = []
if "notes" not in st.session_state:
    st.session_state.notes = []

# ─── SELECTORS ───
st.markdown('<div class="selector-card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    level = st.selectbox("📊 Apna Level Choose Karo", list(LEVELS.keys()))
with col2:
    subject = st.selectbox("📚 Subject Choose Karo", SUBJECTS)
st.markdown('</div>', unsafe_allow_html=True)

# ─── STATS ───
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="metric-card"><h3 style="color:#ffd200">{len(st.session_state.messages)//2}</h3><p style="color:#a0a0c0;font-size:0.8rem">Questions Asked</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><h3 style="color:#22c1c3">{len(st.session_state.notes)}</h3><p style="color:#a0a0c0;font-size:0.8rem">Notes Saved</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><h3 style="color:#667eea">{subject[:12]}</h3><p style="color:#a0a0c0;font-size:0.8rem">Current Subject</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── CHAT ───
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Topic pucho, exam answer maango, ya 'quiz do' likho..."):
    full_prompt = f"Subject: {subject}\nLevel: {level}\nQuestion: {prompt}"
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=[
                {"role": "system", "content": get_system_prompt(level, subject)},
                *[{"role": m["role"], "content": m["content"]}
                  for m in st.session_state.messages[:-1]],
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=1800,
            stream=True
        )
        response = st.write_stream(
            chunk.choices[0].delta.content
            for chunk in stream
            if chunk.choices[0].delta.content
        )

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.notes.append({
        "subject": subject,
        "level": level,
        "question": prompt,
        "answer": response
    })

st.markdown("<br>", unsafe_allow_html=True)

# ─── BUTTONS ───
col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Naya Topic Shuru Karo"):
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.session_state.notes:
        pdf_data = generate_pdf(st.session_state.notes)
        st.download_button(
            label="📥 PDF Notes Download Karo",
            data=pdf_data,
            file_name=f"aadil_mentor_{subject.replace(' ','_')}.pdf",
            mime="application/pdf"
        )
    else:
        st.info("Pehle koi question pucho — phir PDF download hogi!")
