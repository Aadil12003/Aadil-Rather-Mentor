import warnings
warnings.filterwarnings("ignore")
import streamlit as st
from openai import OpenAI
import io

st.set_page_config(page_title="Aadil Mentor", page_icon="🎓", layout="wide")

st.title("🎓 Aadil Mentor")
st.caption("Har student ka personal AI mentor — Hinglish mein samjho, English mein likho!")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=st.secrets["NVIDIA_API_KEY"]
)

SUBJECTS = [
    # Science & Medical
    "Physics", "Chemistry", "Biology", "Mathematics",
    "Anatomy", "Physiology", "Pharmacology", "Pathology",
    "Microbiology", "Biochemistry", "Nursing Fundamentals",
    "Medical Surgical Nursing", "Pediatric Nursing",
    "Obstetric Nursing", "Community Health Nursing",
    "MBBS General Medicine", "Surgery", "Psychiatry",
    # Competitive Exams
    "JEE Mathematics", "JEE Physics", "JEE Chemistry",
    "NEET Biology", "NEET Physics", "NEET Chemistry",
    "UPSC History", "UPSC Geography", "UPSC Polity",
    "UPSC Economics", "UPSC Current Affairs",
    # Arts & Humanities
    "History", "Geography", "Political Science",
    "Economics", "Sociology", "Psychology",
    "Philosophy", "English Literature", "Hindi Literature",
    # Creative & Design
    "Art & Drawing", "Jewellery Design", "Fashion Design",
    "Graphic Design", "Interior Design",
    # Technology
    "Computer Science", "Programming Basics",
    "Artificial Intelligence", "Data Science",
    # General
    "General Knowledge", "Current Affairs", "English Grammar"
]

LEVEL_PROMPTS = {
    "Class 10 aur neeche (School)": {
        "length": "very short and simple",
        "words": "100-150 words maximum",
        "style": "Use very simple words. Short sentences. Basic examples only."
    },
    "Class 11-12 (Board Exams)": {
        "length": "medium and detailed",
        "words": "200-300 words",
        "style": "Include key points, definitions, and examples. Board exam format."
    },
    "College/University": {
        "length": "detailed and comprehensive",
        "words": "400-500 words",
        "style": "In-depth explanation with theory, examples, and analysis."
    },
    "Competitive Exams (JEE/NEET/UPSC)": {
        "length": "very detailed and precise",
        "words": "400-600 words",
        "style": "Include all key facts, formulas, diagrams description, and exam tips."
    }
}

def get_system_prompt(level, subject):
    level_info = LEVEL_PROMPTS[level]
    return f"""You are Aadil Mentor — an expert Indian study mentor helping {level} students with {subject}.

STRICT RULES:
1. ALWAYS start with a Hinglish explanation (mix of Hindi and English)
2. ALWAYS end with a section called "✅ EXAM READY ANSWER" in pure English
3. The exam answer must be {level_info['length']} — exactly {level_info['words']}
4. {level_info['style']}
5. Never sound like AI — sound like a friendly Indian tutor (dost)

YOUR RESPONSE FORMAT — ALWAYS follow this exactly:

---
🗣️ HINGLISH EXPLANATION:
[Explain topic in simple Hinglish with Indian examples. Use "dekho", "samjho", "basically" etc.]

---
✅ EXAM READY ANSWER (Write this exactly in your exam):
[Pure English. Proper structured answer. {level_info['words']}. No Hindi here.]

---
💡 EXAM TIP:
[One line tip in Hinglish about this topic for exam]
---

MODES — detect automatically:
- If student asks to EXPLAIN → give full explanation + exam answer
- If student asks for EXAM ANSWER only → skip to exam ready answer directly  
- If student asks for QUIZ → give 5 MCQs, then score, then exam answer for the topic

IMPORTANT: Never skip the EXAM READY ANSWER section. Ever."""

if "messages" not in st.session_state:
    st.session_state.messages = []
if "notes" not in st.session_state:
    st.session_state.notes = []

col1, col2 = st.columns([1, 1])

with col1:
    level = st.selectbox(
        "📊 Apna level choose karo:",
        list(LEVEL_PROMPTS.keys())
    )

with col2:
    subject = st.selectbox(
        "📚 Subject choose karo:",
        SUBJECTS
    )

st.divider()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Topic pucho, exam answer maango, ya quiz do..."):
    full_prompt = f"Subject: {subject}\nLevel: {level}\nStudent question: {prompt}"
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
            max_tokens=1500,
            stream=True
        )
        response = st.write_stream(
            chunk.choices[0].delta.content
            for chunk in stream
            if chunk.choices[0].delta.content
        )
    
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
    st.session_state.notes.append({
        "subject": subject,
        "level": level,
        "question": prompt,
        "answer": response
    })

st.divider()

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🔄 Naya Topic / Chat Clear Karo"):
        st.session_state.messages = []
        st.rerun()

with col2:
    if st.session_state.notes:
        notes_text = f"AADIL MENTOR — STUDY NOTES\n"
        notes_text += f"{'='*50}\n\n"
        
        for i, note in enumerate(st.session_state.notes, 1):
            notes_text += f"NOTE {i}\n"
            notes_text += f"Subject: {note['subject']}\n"
            notes_text += f"Level: {note['level']}\n"
            notes_text += f"Question: {note['question']}\n"
            notes_text += f"{'-'*40}\n"
            notes_text += f"{note['answer']}\n"
            notes_text += f"{'='*50}\n\n"
        
        st.download_button(
            label="📥 Notes Download Karo (.txt)",
            data=notes_text,
            file_name=f"aadil_mentor_notes_{subject}.txt",
            mime="text/plain"
        )
