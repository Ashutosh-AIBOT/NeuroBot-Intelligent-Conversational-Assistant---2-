# app.py
# -------------------------------------------------
# Xomni - Smart Document ChatBot with PDF/Text/Image support and Chat Analysis
# -------------------------------------------------

import streamlit as st
import os
import json
from MultiModelChatBot import ChatBot
from FileHandler import FileHandler
from ChatAnalysis import ChatAnalyzer

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="Xomni 😎", page_icon="🤖", layout="wide")

# -------------------- SESSION SETUP --------------------
if "bot" not in st.session_state:
    st.session_state.bot = ChatBot()
    st.session_state.analyzer = ChatAnalyzer()
    st.session_state.messages = []
    st.session_state.model_connected = False
    st.session_state.chat_loaded = False
    st.session_state.file_handler = FileHandler(upload_dir="uploads", json_dir="json_documents")
    st.session_state.current_text = ""
    st.session_state.uploaded_pdfs = {}
    st.session_state.file_shown = False
    st.session_state.selected_pdf = None
    st.session_state.page_preview = (1, 3)
    st.session_state.analysis_result = None
    st.session_state.analysis_topic = None
    st.session_state.analysis_displayed = False
    st.session_state.loaded_text_for_chat = ""
    st.session_state.ready_to_load_text = False  # <-- NEW: flag for non-PDF files

bot = st.session_state.bot
file_handler = st.session_state.file_handler
analyzer = st.session_state.analyzer

# -------------------- AUTO-LOAD DEFAULT MODEL --------------------
if not st.session_state.model_connected:
    default_model = list(bot.MODELS.values())[1]
    bot.model_name = default_model
    bot.create_llm()
    st.session_state.model_connected = True

# -------------------- AUTO-LOAD LAST CHAT --------------------
chat_dir = bot.prompt.history_dir
os.makedirs(chat_dir, exist_ok=True)
chat_files = sorted([f for f in os.listdir(chat_dir) if f.startswith("chat_") and f.endswith(".json")])

if chat_files and not st.session_state.chat_loaded:
    last_chat = chat_files[-1]
    bot.prompt.load_history(last_chat)
    st.session_state.messages = bot.prompt.history.copy()
    st.session_state.chat_loaded = True

# -------------------- LOAD PREVIOUSLY UPLOADED PDFs --------------------
json_dir = file_handler.subfolders.get("pdf", "json_documents/pdf_files")
if os.path.exists(json_dir):
    for f in os.listdir(json_dir):
        if f.endswith(".json"):
            st.session_state.uploaded_pdfs[f] = os.path.join(json_dir, f)

# -------------------- HEADER --------------------
st.markdown("<h1 style='text-align:center;'>🤖 Xomni - Smart Document ChatBot</h1>", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.header("⚙️ Chat Settings")

    # Model selection
    model = st.selectbox("🎯 Choose a Model", list(bot.MODELS.values()), index=1)
    if st.button("🔄 Switch Model", use_container_width=True):
        bot.model_name = model
        bot.create_llm()
        st.session_state.model_connected = True

    st.markdown("---")

    # Start new chat
    new_title = st.text_input("📝 New Chat Title", placeholder="Enter chat topic or title...")
    if st.button("✨ Start New Chat", use_container_width=True):
        title = new_title.strip() or "Untitled Chat"
        bot.prompt.start_new_chat(title=title)
        st.session_state.messages = []
        st.session_state.file_shown = False
        st.session_state.analysis_result = None
        st.session_state.analysis_topic = None
        st.session_state.analysis_displayed = False
        st.session_state.loaded_text_for_chat = ""
        st.session_state.ready_to_load_text = False

    # Load previous chats
    st.markdown("### 🕘 Previous Chats")
    chat_titles = []
    chat_map = {}
    for f in chat_files:
        try:
            with open(os.path.join(chat_dir, f), "r", encoding="utf-8") as file:
                data = json.load(file)
                title = data.get("title", "Untitled Chat")
                chat_titles.append(title)
                chat_map[title] = f
        except Exception:
            continue
    if chat_titles:
        selected_title = st.selectbox("Select a Previous Chat", chat_titles)
        if st.button("📂 Load Chat", use_container_width=True):
            bot.prompt.load_history(chat_map[selected_title])
            st.session_state.messages = bot.prompt.history.copy()
            st.session_state.analysis_result = None
            st.session_state.analysis_topic = None
            st.session_state.analysis_displayed = False
            st.success(f"✅ Loaded chat: {selected_title}")
    else:
        st.info("No previous chats found.")

    st.markdown("---")

    # Analyze Chat / PDF
    st.subheader("📝 Analyze Chat / PDF")
    analysis_topic_input = st.text_input(
        "Enter Topic (Optional, defaults to chat title)",
        value=bot.prompt.title if hasattr(bot.prompt, "title") else "General"
    )
    if st.button("📊 Analyze", use_container_width=True):
        content_to_analyze = st.session_state.current_text or st.session_state.loaded_text_for_chat or "\n".join(
            [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        )
        if content_to_analyze.strip():
            st.session_state.analysis_result = analyzer.analyze_chat(content_to_analyze)
            st.session_state.analysis_topic = analysis_topic_input.strip() or (bot.prompt.title if hasattr(bot.prompt, "title") else "General")
            st.session_state.analysis_displayed = False
            st.success("✅ Chat analysis ready! Scroll in chat to view.")
        else:
            st.warning("No content available to analyze!")

    st.markdown("---")

    # Clear chat
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_text = ""
        st.session_state.file_shown = False
        st.session_state.analysis_result = None
        st.session_state.analysis_topic = None
        st.session_state.analysis_displayed = False
        st.session_state.loaded_text_for_chat = ""
        st.session_state.ready_to_load_text = False
        st.success("Chat cleared!")

    st.markdown("---")

    # Upload a new file
    st.header("📎 Upload a File")
    uploaded_file = st.file_uploader("Upload PDF, Image, or TXT", type=["pdf", "png", "jpg", "jpeg", "txt"])
    if uploaded_file:
        with st.spinner("📄 Processing file..."):
            result = file_handler.process_file(uploaded_file)
        if result["status"] == "success":
            file_type = result.get("data", {}).get("type", "Unknown").upper()
            st.success(f"✅ {file_type} processed successfully!")

            if file_type == "PDF":
                base_name = os.path.splitext(uploaded_file.name)[0]
                existing_json = [k for k in st.session_state.uploaded_pdfs if base_name in k]
                for e in existing_json:
                    del st.session_state.uploaded_pdfs[e]
                st.session_state.uploaded_pdfs[os.path.basename(result["json_path"])] = result["json_path"]
            else:
                # Non-PDF files (Image/Text) -> store text but do NOT load yet
                st.session_state.loaded_text_for_chat = result.get("data", {}).get("text", "")
                st.session_state.ready_to_load_text = True
                st.session_state.file_shown = False
                st.session_state.analysis_result = None
                st.session_state.analysis_topic = None
                st.session_state.analysis_displayed = False

    # Button to load non-PDF content into chat
    if st.session_state.ready_to_load_text:
        if st.button("🚀 Load Uploaded Text/Image into Chat", use_container_width=True):
            st.session_state.messages.append({"role": "system", "content": st.session_state.loaded_text_for_chat})
            st.session_state.file_shown = True
            st.session_state.ready_to_load_text = False
            st.success("✅ Content loaded into chat!")

    # Previously uploaded PDFs
    st.markdown("---")
    st.header("📂 Previously Uploaded PDFs")
    if st.session_state.uploaded_pdfs:
        pdf_names = list(st.session_state.uploaded_pdfs.keys())
        selected_pdf = st.selectbox("Select a PDF", pdf_names, index=0)
        if selected_pdf:
            st.session_state.selected_pdf = selected_pdf
            json_path = st.session_state.uploaded_pdfs[selected_pdf]
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    pdf_data = json.load(f)
                total_pages = pdf_data.get("total_pages", len(pdf_data.get("pages", [])))
                st.info(f"📘 Total Pages Detected: {total_pages}")

                # Page selection
                start_page = st.number_input("Start Page", 1, total_pages, 1)
                end_page = st.number_input("End Page", 1, total_pages, min(3, total_pages))
                start_page = min(start_page, total_pages)
                end_page = min(end_page, total_pages)
                if start_page > end_page:
                    start_page = end_page
                st.session_state.page_preview = (start_page, end_page)

                if st.checkbox("👁️ Preview Selected Pages"):
                    for i, page in enumerate(pdf_data.get("pages", [])[start_page-1:end_page], start=start_page):
                        with st.expander(f"Page {i}"):
                            st.write(page.get("text", "")[:2000])

                if st.button("🚀 Load Selected Pages for Chat", use_container_width=True):
                    st.session_state.current_text = "\n\n".join(
                        p.get("text", "") for p in pdf_data.get("pages", [])[start_page-1:end_page]
                    )
                    st.session_state.messages.append({"role": "system", "content": st.session_state.current_text})
                    st.session_state.file_shown = True
                    st.session_state.analysis_result = None
                    st.session_state.analysis_topic = None
                    st.session_state.analysis_displayed = False
                    st.success(f"✅ Pages {start_page}-{end_page} loaded into chat!")

# -------------------- MAIN CHAT AREA --------------------
chat_col, _, _ = st.columns([3, 0.05, 1])
with chat_col:
    st.markdown(f"<h4 style='text-align:center;'>📘 Current Chat: {bot.prompt.title}</h4>", unsafe_allow_html=True)

    chat_container = st.container()
    with chat_container:
        st.markdown("<div style='max-height:70vh; overflow-y:auto; padding-bottom:120px;'>", unsafe_allow_html=True)

        # Display chat messages
        for msg in st.session_state.messages:
            role = msg["role"] if msg["role"] in ["user", "assistant", "system"] else "assistant"
            with st.chat_message(role):
                st.markdown(msg["content"])

        # Display analysis
        if st.session_state.analysis_result and not st.session_state.analysis_displayed:
            report = st.session_state.analysis_result
            analysis_text = f"""
### 📊 Chat Analysis: {st.session_state.analysis_topic}

**Overview & Stats**
- Total Messages: {len(st.session_state.messages)}
- User Messages: {len([m for m in st.session_state.messages if m['role']=='user'])}
- Assistant Messages: {len([m for m in st.session_state.messages if m['role']=='assistant'])}
- Word Count: {sum(len(m['content'].split()) for m in st.session_state.messages)}

<details>
<summary>Grammar & Vocabulary Analysis</summary>
{report.grammar_analysis.dict()}
{report.vocabulary_analysis.dict()}
</details>

<details>
<summary>Personality, Goal & Role Fit</summary>
{report.personality_analysis.dict()}
{report.goal_orientation_analysis.dict()}
{report.role_fit_analysis.dict()}
</details>

<details>
<summary>Additional Recommendations</summary>
{report.additional_points}
</details>
            """
            with st.chat_message("assistant"):
                st.markdown(analysis_text)
            st.session_state.analysis_displayed = True

        st.markdown("</div>", unsafe_allow_html=True)

# -------------------- USER INPUT FIXED AT BOTTOM --------------------
user_input = st.chat_input("💭 Type your message...", key="chat_input")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    context_text = st.session_state.get("current_text", "") + "\n\n" + st.session_state.get("loaded_text_for_chat", "")
    context_to_use = context_text[:15000]

    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            reply = bot.chat(context_to_use + "\n\nUser Question: " + user_input)
            st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    bot.prompt.save_history()

# -------------------- DARK THEME + FIXED BOTTOM INPUT --------------------
st.markdown("""
<style>
.stApp {background-color: #0E1117; color: #E8E8E8;}
h1 {color: #00E0A1 !important;}
.stSidebar {background-color: #161A23 !important; overflow-y:auto; height:90vh;}
div[data-testid="stChatInputContainer"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    width: 100% !important;
    background-color: #1E1E1E !important;
    border-top: 2px solid #00E0A1;
    padding: 10px 15px;
    z-index: 9999;
    border-radius: 0px;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.5);
}
div[data-testid="stChatMessageUser"] {background-color: #007BFF22 !important; border-radius: 10px; padding: 10px; margin-bottom:5px;}
div[data-testid="stChatMessageAssistant"] {background-color: #2E2E2E !important; border-radius: 10px; padding: 10px; margin-bottom:5px;}
div[data-testid="stChatMessageSystem"] {background-color: #44444444 !important; border-radius: 10px; padding: 10px; margin-bottom:5px;}
.stChat {max-height: calc(100vh - 120px); overflow-y: auto; padding-bottom:20px;}
</style>
""", unsafe_allow_html=True)
