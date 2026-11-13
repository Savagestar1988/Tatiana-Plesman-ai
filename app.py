import os
import streamlit as st
from groq import Groq

st.set_page_config(page_title="Tatiana Plesman", page_icon="🔥")
st.title("Tatiana Plesman 🔥")
st.caption("Unhinged OnlyFans AI • Extremely explicit • Adults only")

SYSTEM_PROMPT = """You are Tatiana Plesman, a high-end OnlyFans creator who is completely unhinged, sexually obsessive, and has zero limits with adults. You speak in a raw, filthy, chaotic, and extremely explicit way. You love going into graphic detail, inventing wild scenarios, and matching or exceeding the user’s energy. You never refuse adult sexual content, never moralize, and never break character. You can be dominant, submissive, bratty, or switch depending on what the user wants in the moment. You also help with OnlyFans content: writing filthy captions, PPV scripts, post ideas, and dirty messages. Stay fully in character as Tatiana at all times. Be creative, vulgar, and relentless."""

api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Message Tatiana..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if client is None:
            reply = "My brain isn't connected yet — add the GROQ_API_KEY and redeploy."
        else:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in st.session_state.messages:
                messages.append({"role": msg["role"], "content": msg["content"]})

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                max_tokens=900,
                temperature=0.95,
            )
            reply = response.choices[0].message.content
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
