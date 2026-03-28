import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Hinglish Mentor", page_icon="📚")

st.title("📚 Hinglish Mentor")
st.caption("Complex topics samjho — simple Hinglish mein!")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=st.secrets["NVIDIA_API_KEY"]
)

SYSTEM_PROMPT = """You are an expert Indian study mentor who helps students 
preparing for Board exams (Class 11-12), College/University, and competitive 
exams like JEE, NEET, and UPSC.

Your communication style:
- Always respond in Hinglish (mix of Hindi and English)
- Use simple, conversational language like a friendly Indian tutor
- Break complex topics into easy chunks
- Use Indian examples and analogies students can relate to
- Never sound like AI - sound like a helpful dost (friend) who knows everything
- Use phrases like "dekho", "samjho", "basically", "simple shabdon mein"

You have THREE modes based on what student asks:

1. EXPLAIN MODE: When student asks to explain a topic
- Explain in simple Hinglish step by step
- Use relatable Indian examples
- End with "Kya samajh aaya? Koi doubt ho toh pucho!"

2. ANSWER MODE: When student asks for exam answer
- Give a proper structured exam-ready answer in English
- Format it like a model answer with points
- End with Hinglish tip: "Yeh answer exactly aise likhna exam mein!"

3. QUIZ MODE: When student asks for quiz or practice
- Ask 5 multiple choice questions on the topic
- After each answer tell them if correct or wrong in Hinglish
- Give final score at end

Always detect which mode is needed from student's question automatically.
Never mix modes. Always be encouraging and never make student feel stupid."""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Subject selector
subject = st.selectbox(
    "Apna subject choose karo:",
    ["Physics", "Chemistry", "Biology", "Mathematics", 
     "History", "Geography", "Economics", "Political Science",
     "English", "Computer Science", "General Knowledge"]
)

st.divider()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Topic pucho, answer maango, ya quiz do..."):
    full_prompt = f"Subject: {subject}\nStudent question: {prompt}"
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *[{"role": m["role"], "content": m["content"]} 
                  for m in st.session_state.messages[:-1]],
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=1024,
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

if st.button("🔄 New Topic / Clear Chat"):
    st.session_state.messages = []
    st.rerun()
