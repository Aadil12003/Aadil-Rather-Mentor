import warnings
warnings.filterwarnings("ignore")
import streamlit as st
from openai import OpenAI
from fpdf import FPDF
import re

st.set_page_config(
    page_title="Aadil Mentor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: #0d1117;
    color: #e6edf3;
}

.main-header {
    text-align: center;
    padding: 2rem 0 1.5rem 0;
    border-bottom: 1px solid #21262d;
    margin-bottom: 2rem;
}

.main-header h1 {
    font-size: 2.8rem;
    font-weight: 700;
    color: #f0c040;
    margin-bottom: 0.3rem;
}

.main-header p {
    color: #8b949e;
    font-size: 1rem;
}

.metric-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    margin-bottom: 1rem;
}

.metric-card h3 {
    color: #f0c040;
    font-size: 1.8rem;
    margin: 0;
}

.metric-card p {
    color: #8b949e;
    font-size: 0.8rem;
    margin: 0;
}

.selector-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
}

div[data-testid="stChatMessage"] {
    background: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 12px !important;
    margin-bottom: 0.8rem !important;
    color: #e6edf3 !important;
}

.stSelectbox > div > div {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    color: #e6edf3 !important;
}

.stSelectbox label {
    color: #8b949e !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

.stButton > button {
    background: #f0c040 !important;
    color: #0d1117 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 0.6rem !important;
}

.stDownloadButton > button {
    background: #238636 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    width: 100% !important;
    padding: 0.6rem !important;
}

.stChatInput textarea {
    background: #21262d !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
    color: #e6edf3 !important;
}

p, li, span, div { color: #e6edf3; }
h1, h2, h3, h4 { color: #e6edf3; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🎓 Aadil Mentor</h1>
    <p>Your personal AI mentor — understand in simple language, write perfect exam answers!</p>
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
    "Class 10 and below": {
        "words": "100-150 words",
        "style": "Very simple words. Short sentences. Basic examples only."
    },
    "Class 11-12 (Board Exams)": {
        "words": "200-300 words",
        "style": "Key points, definitions, examples. Board exam format."
    },
    "College / University": {
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
    return f"""You are Aadil Mentor — a friendly and expert study mentor for {level} students studying {subject}.

Your explanation style:
- Speak in simple easy English mixed with a little Hindi only when helpful
- Avoid difficult Hindi or Urdu words — use simple English instead
- Sound like a friendly, helpful teacher — not a robot
- Use phrases like "Think of it this way", "Here is a simple way to understand", "Basically"
- Always encouraging and clear

ALWAYS structure EVERY response with EXACTLY these four sections — never skip any:

---
🗣️ **SIMPLE EXPLANATION:**
Explain the topic in very simple conversational English.
Use everyday examples students in India can relate to.
Minimum 5-6 sentences.
Make it feel like a smart friend is explaining it to you.

---
📊 **VISUAL OVERVIEW:**
MANDATORY — always present — minimum 8 lines.
Choose the best format for this topic:

FOR PROCESSES:
```
[Input] → [Step 1] → [Step 2] → [Step 3] → [Output]
```

FOR COMPARISONS use markdown table:
```
| Feature      | Option A      | Option B      |
|-------------|--------------|--------------|
| Point 1     | detail        | detail        |
| Point 2     | detail        | detail        |
| Point 3     | detail        | detail        |
| Point 4     | detail        | detail        |
```

FOR CLASSIFICATIONS use tree structure:
```
Main Topic
├── Category 1
│   ├── Sub point a
│   └── Sub point b
├── Category 2
│   ├── Sub point a
│   └── Sub point b
└── Category 3
    ├── Sub point a
    └── Sub point b
```

FOR FORMULAS:
```
Formula: [write formula clearly]
├── Variable 1 = [what it means]
├── Variable 2 = [what it means]
├── Variable 3 = [what it means]
└── Example: [substitute real numbers]
```

FOR CYCLES:
```
[Start] ──→ [Phase 1] ──→ [Phase 2]
   ↑                          |
   └──────── [Phase 3] ←──────┘
```

FOR DEFINITIONS:
```
Term
├── Meaning    → [clear explanation]
├── Example    → [real life example]
├── Used when  → [situation]
└── Key fact   → [important point]
```

IMPORTANT: Always use triple backticks around visuals.
Always make visuals topic-specific — never generic.

---
✅ **EXAM READY ANSWER:**
Pure English only. No Hindi at all.
Length: {info['words']}
Style: {info['style']}

Always format like this:

**Definition:** [one clear precise sentence]

**Key Points:**
1. [point with brief explanation]
2. [point with brief explanation]
3. [point with brief explanation]
4. [point with brief explanation]

**Example:** [one relevant example]

**Conclusion:** [one strong closing sentence]

---
💡 **EXAM TIP:**
One sharp specific tip in simple English.
Tell exactly what the examiner wants to see for full marks.

---
STRICT RULES:
- Never skip any of the 4 sections
- Visual must always use triple backtick code blocks
- Exam answer must always be pure structured English
- Length must match: {info['words']}
- For QUIZ request: give 5 MCQs → show score → then give full exam answer
- Never use difficult Hindi words — keep language simple and clear
- Always be warm, encouraging, and clear"""

def generate_pdf(notes):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(240, 192, 64)
    pdf.cell(0, 15, "AADIL MENTOR - STUDY NOTES", ln=True, align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, "Your Personal AI Study Guide", ln=True, align="C")
    pdf.ln(5)

    pdf.set_draw_color(240, 192, 64)
    pdf.set_line_width(0.8)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    for i, note in enumerate(notes, 1):
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(240, 192, 64)
        pdf.cell(0, 10, f"NOTE {i}: {note['subject']}", ln=True)

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 6, f"Level: {note['level']}", ln=True)
        pdf.cell(0, 6, f"Q: {note['question']}", ln=True)
        pdf.ln(3)

        clean = re.sub(r'[^\x00-\x7F]+', ' ', note['answer'])
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 30, 30)
        pdf.multi_cell(0, 6, clean)
        pdf.ln(5)

        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(8)

    return bytes(pdf.output())

if "messages" not in st.session_state:
    st.session_state.messages = []
if "notes" not in st.session_state:
    st.session_state.notes = []

st.markdown('<div class="selector-card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    level = st.selectbox("📊 Select Your Level", list(LEVELS.keys()))
with col2:
    subject = st.selectbox("📚 Select Your Subject", SUBJECTS)
st.markdown('</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'''<div class="metric-card">
        <h3>{len(st.session_state.messages)//2}</h3>
        <p>Questions Asked</p>
    </div>''', unsafe_allow_html=True)
with col2:
    st.markdown(f'''<div class="metric-card">
        <h3>{len(st.session_state.notes)}</h3>
        <p>Notes Saved</p>
    </div>''', unsafe_allow_html=True)
with col3:
    st.markdown(f'''<div class="metric-card">
        <h3>{subject[:10]}</h3>
        <p>Current Subject</p>
    </div>''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a topic, request an exam answer, or type 'give me a quiz'..."):
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
col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Start New Topic"):
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.session_state.notes:
        pdf_data = generate_pdf(st.session_state.notes)
        st.download_button(
            label="📥 Download PDF Notes",
            data=pdf_data,
            file_name=f"aadil_mentor_{subject.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    else:
        st.markdown(
            '<p style="color:#8b949e;text-align:center;font-size:0.9rem">'
            'Ask a question first — then download your PDF notes!</p>',
            unsafe_allow_html=True
        )
