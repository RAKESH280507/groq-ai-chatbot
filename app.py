import os
import uuid
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# ---------------- CONFIGURATION ----------------

load_dotenv()

st.set_page_config(
    page_title="Nexus AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not API_KEY:
    st.error("GROQ_API_KEY is missing. Add it to your .env file.")
    st.stop()

client = Groq(api_key=API_KEY)


# ---------------- SESSION STATE ----------------

if "chats" not in st.session_state:
    st.session_state.chats = {}

if "active_chat" not in st.session_state:
    st.session_state.active_chat = None

if "theme" not in st.session_state:
    st.session_state.theme = "System"

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


def create_chat():
    chat_id = str(uuid.uuid4())

    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "messages": []
    }

    st.session_state.active_chat = chat_id


if not st.session_state.chats:
    create_chat()


# ---------------- THEME ----------------

theme = st.session_state.theme

if theme == "Dark":
    background = "#0E1117"
    panel = "#161B22"
    text = "#F0F3F6"
    muted = "#9CA3AF"
    border = "#30363D"
    user_bubble = "#243247"
elif theme == "Light":
    background = "#FFFFFF"
    panel = "#F5F7FA"
    text = "#202124"
    muted = "#646B75"
    border = "#E1E5EB"
    user_bubble = "#E8F0FE"
else:
    # Use the browser/OS preference as a practical default.
    background = "light-dark(#FFFFFF, #0E1117)"
    panel = "light-dark(#F5F7FA, #161B22)"
    text = "light-dark(#202124, #F0F3F6)"
    muted = "light-dark(#646B75, #9CA3AF)"
    border = "light-dark(#E1E5EB, #30363D)"
    user_bubble = "light-dark(#E8F0FE, #243247)"

st.markdown(
    f"""
    <style>
    :root {{
        color-scheme: light dark;
    }}

    .stApp {{
        background: {background};
        color: {text};
    }}

    [data-testid="stSidebar"] {{
        background: {panel};
        border-right: 1px solid {border};
    }}

    .block-container {{
        max-width: 950px;
        padding-top: 2rem;
        padding-bottom: 7rem;
    }}

    .brand {{
        font-size: 1.65rem;
        font-weight: 800;
        letter-spacing: -0.7px;
        padding: 0.4rem 0 1.1rem;
    }}

    .subtitle {{
        color: {muted};
        font-size: 0.9rem;
    }}

    .welcome {{
        text-align: center;
        padding: 12vh 0 3rem;
    }}

    .welcome h1 {{
        font-size: clamp(2rem, 5vw, 3.2rem);
        font-weight: 800;
        letter-spacing: -1.5px;
    }}

    .welcome p {{
        color: {muted};
        font-size: 1.05rem;
    }}

    [data-testid="stChatMessage"] {{
        border-radius: 14px;
        padding: 1rem;
    }}

    .stButton > button {{
        border-radius: 10px;
        min-height: 2.5rem;
    }}

    [data-testid="stChatInput"] {{
        border-radius: 14px;
    }}

    .footer {{
        color: {muted};
        text-align: center;
        font-size: 0.8rem;
        padding: 1rem 0;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown('<div class="brand">✦ Nexus AI</div>',
                unsafe_allow_html=True)

    st.caption("YOUR PERSONAL AI ASSISTANT")

    if st.button("＋  New Chat", use_container_width=True,
                 type="primary"):
        create_chat()
        st.rerun()

    st.divider()

    st.markdown("##### RECENT CONVERSATIONS")

    # Newest chats first
    chat_ids = list(st.session_state.chats.keys())[::-1]

    for chat_id in chat_ids:
        chat = st.session_state.chats[chat_id]
        col1, col2 = st.columns([5, 1])

        with col1:
            label = chat["title"][:27]
            if chat_id == st.session_state.active_chat:
                label = "● " + label

            if st.button(
                label,
                key=f"open_{chat_id}",
                use_container_width=True
            ):
                st.session_state.active_chat = chat_id
                st.rerun()

        with col2:
            if st.button("×", key=f"delete_{chat_id}",
                         help="Delete conversation"):
                del st.session_state.chats[chat_id]

                if st.session_state.active_chat == chat_id:
                    st.session_state.active_chat = (
                        next(iter(st.session_state.chats), None)
                    )

                if st.session_state.active_chat is None:
                    create_chat()

                st.rerun()

    st.divider()

    st.markdown("##### APPEARANCE")

    selected_theme = st.selectbox(
        "Theme",
        ["System", "Light", "Dark"],
        index=["System", "Light", "Dark"].index(
            st.session_state.theme
        )
    )

    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.rerun()

    st.caption("System mode follows the browser's color preference.")

    st.divider()
    st.caption("Powered by Groq · Built with Streamlit")


# ---------------- ACTIVE CHAT ----------------

active_id = st.session_state.active_chat

if active_id not in st.session_state.chats:
    create_chat()
    active_id = st.session_state.active_chat

chat = st.session_state.chats[active_id]


# ---------------- CHAT HEADER ----------------

st.markdown("### ✦ Nexus AI")
st.markdown(
    '<div class="subtitle">Your ideas, one conversation away.</div>',
    unsafe_allow_html=True
)

st.divider()


# ---------------- WELCOME SCREEN ----------------

if not chat["messages"]:
    st.markdown(
        """
        <div class="welcome">
            <h1>What can I help with?</h1>
            <p>Ask a question, explore an idea, or solve a problem.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    prompts = [
        "Explain machine learning",
        "Help me write Python code",
        "Give me project ideas"
    ]

    cols = st.columns(3)

    for i, prompt in enumerate(prompts):
        if cols[i].button(prompt, use_container_width=True):
            st.session_state.pending_prompt = prompt
            st.rerun()


# ---------------- DISPLAY CHAT HISTORY ----------------

for message in chat["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------- CHAT INPUT ----------------

prompt = st.chat_input("Message Nexus AI...")

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None


# ---------------- GROQ RESPONSE ----------------

if prompt:
    chat["messages"].append({
        "role": "user",
        "content": prompt
    })

    if chat["title"] == "New Chat":
        chat["title"] = prompt[:30]

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are Nexus AI, a helpful, friendly "
                                "and accurate assistant. Use Markdown "
                                "for clear answers. Format code using "
                                "appropriate code fences."
                            )
                        },
                        *chat["messages"]
                    ],
                    temperature=0.7,
                    max_completion_tokens=2048
                )

                answer = response.choices[0].message.content

                if not answer:
                    answer = "I couldn't generate a response. Please try again."

                st.markdown(answer)

            chat["messages"].append({
                "role": "assistant",
                "content": answer
            })

        except Exception as error:
            st.error("Unable to get a response from Groq.")
            st.caption(
                "Check your API key, model name, internet connection, "
                "and API usage limits."
            )
            # Remove the unanswered user message so it can be retried.
            chat["messages"].pop()

            print(f"Groq API error: {error}")

    st.rerun()


# ---------------- FOOTER ----------------

st.markdown(
    '<div class="footer">Nexus AI · AI can make mistakes. Verify important information.</div>',
    unsafe_allow_html=True
)
