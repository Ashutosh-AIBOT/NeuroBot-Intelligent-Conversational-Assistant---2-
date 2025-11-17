from pydantic import BaseModel, Field
from typing import List, Dict
import json, os
from datetime import datetime


class ChatPrompt(BaseModel):
    """Chat prompt manager with history saving and loading (simple + stable)."""
    system_message: str = Field(default="You are a helpful AI assistant.")
    history: List[Dict[str, str]] = Field(default_factory=list)
    history_dir: str = Field(default="chat_history")
    history_file: str = Field(default="")
    title: str = Field(default="Untitled Chat")

    # ---------- Initialization ----------
    def __init__(self, **data):
        super().__init__(**data)
        os.makedirs(self.history_dir, exist_ok=True)

        # ✅ Load last chat automatically if available
        files = sorted(os.listdir(self.history_dir))
        if files:
            self.load_history(files[-1])  # Load most recent chat
        else:
            # If no chat exists, create one manually
            self.start_new_chat()

    # ---------- Message Handling ----------
    def add_message(self, role: str, content: str):
        """Add message and save immediately."""
        self.history.append({"role": role, "content": content})
        self.save_history()

    def build_prompt(self) -> str:
        """Combine system + message history into one string."""
        lines = [f"System: {self.system_message}"]
        lines += [f"{m['role'].capitalize()}: {m['content']}" for m in self.history]
        lines.append("Assistant:")
        return "\n".join(lines)

    # ---------- File Handling ----------
    def _generate_filename(self):
        """Create unique file name using title + timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_title = self.title.replace(" ", "_").replace("/", "_")
        return f"chat_{safe_title}_{timestamp}.json"

    def save_history(self):
        """Save chat history and title into JSON file."""
        if not self.history_file:
            self.history_file = self._generate_filename()
        path = os.path.join(self.history_dir, self.history_file)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {"title": self.title, "history": self.history},
                f,
                ensure_ascii=False,
                indent=4
            )

    def load_history(self, file_name: str = None):
        """Load chat history by filename or latest one."""
        if not file_name:
            files = sorted(os.listdir(self.history_dir))
            if not files:
                return
            file_name = files[-1]
        path = os.path.join(self.history_dir, file_name)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.title = data.get("title", "Untitled Chat")
                self.history = data.get("history", [])
            self.history_file = file_name

    def start_new_chat(self, title: str = "Untitled Chat"):
        """Start a new chat with a title."""
        self.title = title
        self.history = []
        self.history_file = self._generate_filename()
        self.save_history()

    # ---------- Display ----------
    def show_history(self) -> str:
        """Return chat history in readable text format."""
        if not self.history:
            return "No chat history yet."
        return "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in self.history)
