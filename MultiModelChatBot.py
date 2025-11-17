from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os, sys
from ChatPrompt import ChatPrompt

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_API_KEY")


class ChatBot:
    """A simple multi-model chatbot with JSON history + new chat + load previous chat feature."""
    MODELS = {
        "1": "meta-llama/llama-3-70b-instruct",
        "2": "openai/gpt-4o-mini",
        "3": "mistralai/mixtral-8x7b-instruct",
        "4": "anthropic/claude-3.5-sonnet",
        "5": "google/gemini-pro"
    }

    def __init__(self):
        self.model_name = None
        self.llm = None
        self.prompt = ChatPrompt()

    # -------- Model Handling --------
    def show_models(self):
        print("\n🔸 Available Models:\n")
        for num, name in self.MODELS.items():
            print(f" {num}. {name}")
        print()

    def choose_model(self):
        self.show_models()
        choice = input("👉 Enter model number: ").strip()
        self.model_name = self.MODELS.get(choice, "meta-llama/llama-3-70b-instruct")
        print(f"\n✅ Using model: {self.model_name}\n")

    def create_llm(self):
        try:
            print(f"🔹 Connecting to {self.model_name} ...")
            self.llm = ChatOpenAI(model=self.model_name, temperature=0.7)
            self.llm.invoke("Hello")  # connection test
            print(f"✅ Model {self.model_name} connected!\n")
        except Exception as e:
            print(f"❌ Error: {e}")
            self.llm = None

    # -------- Chat Handling --------
    def chat(self, user_input: str) -> str:
        if not self.llm:
            raise ValueError("⚠️ Model not initialized. Run create_llm() first.")
        self.prompt.add_message("user", user_input)
        full_prompt = self.prompt.build_prompt()
        response = self.llm.invoke(full_prompt)
        reply = response.content
        self.prompt.add_message("assistant", reply)
        return reply

    # -------- History Handling --------
    def new_chat(self):
        """Start a completely new chat (clears history + creates new JSON)."""
        self.prompt.start_new_chat()
        print(f"🆕 Started a new chat file: {self.prompt.history_file}")

    def show_history(self):
        """Show current chat history."""
        print("\n📜 Chat History:\n")
        print(self.prompt.show_history())
        print()

    def list_previous_chats(self):
        """Return a list of all previous chat history JSON files."""
        try:
            files = sorted(os.listdir(self.prompt.history_dir))
            return files if files else []
        except FileNotFoundError:
            return []

    def load_previous_chat(self, file_name: str):
        """Load a specific previous chat by filename."""
        try:
            self.prompt.load_history(file_name)
            print(f"📂 Loaded previous chat: {file_name}")
        except Exception as e:
            print(f"⚠️ Could not load chat {file_name}: {e}")


# -------- Run in Terminal --------
if __name__ == "__main__":
    bot = ChatBot()
    bot.choose_model()
    bot.create_llm()

    if not bot.llm:
        print("⚠️ Falling back to openai/gpt-4o-mini ...")
        bot.model_name = "openai/gpt-4o-mini"
        bot.create_llm()

    print("\n🤖 Multi-Model ChatBot (Type 'history' to view chat, 'new' to start new, 'list' to view past chats, 'load <file>' to load one, 'exit' to quit)\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye! Chats saved in /chat_history/.")
            break

        elif user_input.lower() == "history":
            bot.show_history()
            continue

        elif user_input.lower() == "new":
            bot.new_chat()
            continue

        elif user_input.lower() == "list":
            chats = bot.list_previous_chats()
            if chats:
                print("\n📂 Available chats:")
                for f in chats:
                    print("  -", f)
            else:
                print("No previous chats found.")
            continue

        elif user_input.lower().startswith("load "):
            filename = user_input.split(" ", 1)[1]
            bot.load_previous_chat(filename)
            continue

        try:
            reply = bot.chat(user_input)
            print(f"Bot: {reply}\n")
        except Exception as e:
            print(f"⚠️ Error: {e}\n")
