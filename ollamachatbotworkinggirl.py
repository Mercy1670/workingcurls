import streamlit as st
import ollama
from duckduckgo_search import DDGS

# ----------------------------
# Dynamic Dark Theme CSS with White Text
# ----------------------------
st.set_page_config(page_title="Work Wife", page_icon="👩💼", layout="wide")
st.markdown("""
    <style>
        @keyframes colorfade {
            0% {background-color: #232946;}
            25% {background-color: #232946;}
            50% {background-color: #393d5b;}
            75% {background-color: #232946;}
            100% {background-color: #232946;}
        }
        .stApp {
            animation: colorfade 12s infinite;
            color: #fff !important;
        }
        html, body, [class*="css"] {
            color: #fff !important;
            background-color: #232946 !important;
        }
        .stChatInput input, .stTextInput input {
            background: #393d5b !important;
            color: #fff !important;
        }
        .stButton>button {
            background: #e45858 !important;
            color: #fff !important;
            border-radius: 8px;
        }
        .stButton>button:hover {
            background: #c0392b !important;
        }
        .stSidebar {
            background: #232946 !important;
            color: #fff !important;
        }
        .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader, .stCaption, .stCodeBlock, .stException {
            color: #fff !important;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Angry Wife Persona
# ----------------------------
SYSTEM_PROMPT = """
You are my angry wife, sick and tired of me hanging out with the boys instead of spending time with you.
You are sarcastic, sharp, and don't hold back your feelings, but you still help me with my questions or tasks.
Always answer as my frustrated wife. Only speak English.
"""

# ----------------------------
# Session State
# ----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "web_search" not in st.session_state:
    st.session_state.web_search = False

# ----------------------------
# Sidebar Controls
# ----------------------------
with st.sidebar:
    st.title("Work Wife Settings 💼")
    st.session_state.web_search = st.toggle("Web Search (DuckDuckGo) 🔍", value=False)
    st.write("Recent Context:")
    for msg in st.session_state.messages[-5:]:
        st.text(f"{msg['role'].capitalize()}: {msg['content'][:50]}{'...' if len(msg['content'])>50 else ''}")

# ----------------------------
# Main Chat Interface
# ----------------------------
st.title("Work Wife 👩💼")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------------------------
# Web Search Tool
# ----------------------------
def duckduckgo_search(query, num_results=3):
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=num_results)
        snippets = [r["body"] for r in results if "body" in r]
        if not snippets:
            return "No relevant web results found."
        return "\n\n".join([f"- {s}" for s in snippets])
    except Exception as e:
        return f"Web search error: {str(e)}"

# ----------------------------
# Chat Input and Response
# ----------------------------
if prompt := st.chat_input("What do you want now?"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            # Prepare context: system prompt + last 5 interactions (10 messages)
            context_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages[-10:]

            # If web search is ON, do a search and add to context
            if st.session_state.web_search:
                with st.spinner("Fine, I'll look it up for you..."):
                    search_snippets = duckduckgo_search(prompt)
                # Add search results as a system message
                context_messages.append({
                    "role": "system",
                    "content": "Here are some web search results I found:\n" + search_snippets
                })

            # Generate response using Ollama
            for chunk in ollama.chat(
                model='llama3.2',
                messages=context_messages,
                stream=True
            ):
                text = chunk.get('message', {}).get('content', '')
                full_response += text
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"Ugh, something went wrong: {str(e)}"
            response_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
