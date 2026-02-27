

# 🤖 NeuroBot – Intelligent Conversational Assistant

NeuroBot is an advanced AI-powered conversational assistant designed to analyze chat data, maintain context, and deliver intelligent, multi-model responses. Built with Streamlit, PyTorch/LLMs, and custom NLP pipelines, NeuroBot aims to provide seamless human-AI interaction across text, documents, and uploaded files.

---

## ✨ Key Features

### 🧠 **Context-Aware Chatting**

* Remembers previous messages
* Processes long conversations
* Generates human-like replies using multi-model pipelines

### 📊 **Chat Analytics**

* Word frequency visualization
* User chat behavior insights
* Sentiment and intent scoring

### 📁 **Smart Document Handling**

* Upload PDFs, text files, JSON documents
* Auto-processing & extraction
* Converts data into model-ready format

### 🔗 **Multi-Model Processing**

Uses a custom architecture (`MultiModelChatBot.py`) supporting:

* LLM-based text generation
* Text classification
* Information retrieval
* Prompt chaining

### 🎨 **Beautiful Streamlit UI**

* Modern chat interface
* File upload panels
* Analytics dashboard
* Smooth interaction

---

## 🧱 Project Structure

```
NeuroBot
│
├── main.py                      # Streamlit app entry point
├── MultiModelChatBot.py         # Core multi-model AI engine
├── ChatPrompt.py                # Prompt templates & formatting
├── ChatAnalysis.py              # NLP analytics module
├── FileHandler.py               # Upload & document pre-processing
│
├── chat_history/                # Stored conversations
├── uploads/                     # User uploaded files
├── json_documents/              # Processed JSON outputs
├── processed_json/              # Transformed documents for LLM
│
└── requirements.txt             # Dependencies
└── README.md                    # Project documentation
```

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository

```bash
git clone <your-repo-url>
cd NeuroBot
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Application

```bash
streamlit run main.py
```

---

## 📦 Requirements (Summary)

Key libraries used:

* `streamlit`
* `pandas`
* `matplotlib`, `seaborn`
* `wordcloud`
* `emoji`
* `urlextract`
* `torch` / `transformers` (if using LLMs)
* Custom modules: ChatPrompt, FileHandler, MultiModelChatBot, etc.

---

## 💬 Contact

For collaborations or queries:

**👤 Ashutosh**
---

