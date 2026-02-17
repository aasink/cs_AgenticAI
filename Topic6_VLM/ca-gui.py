import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import asyncio

# import your existing agent
from chatAgent import agent 

from langchain_core.messages import HumanMessage


# --- async wrapper for LangGraph ---
async def run_agent_async(user_text):
    result = await agent.ainvoke({"messages": [HumanMessage(content=user_text)]})
    return result["messages"][-1].content


def run_agent(user_text, callback):
    async def runner():
        reply = await run_agent_async(user_text)
        callback(reply)

    asyncio.run(runner())


# --- Tkinter GUI ---
class ChatUI:
    def __init__(self, root):
        self.root = root
        root.title("LangGraph Chatbot")

        self.chat_log = ScrolledText(root, wrap=tk.WORD, width=60, height=20)
        self.chat_log.pack(padx=10, pady=10)

        self.entry = tk.Entry(root, width=50)
        self.entry.pack(side=tk.LEFT, padx=10, pady=10)
        self.entry.bind("<Return>", self.send_message)

        self.send_btn = tk.Button(root, text="Send", command=self.send_message)
        self.send_btn.pack(side=tk.LEFT)

    def send_message(self, event=None):
        user_text = self.entry.get().strip()
        if not user_text:
            return

        self.chat_log.insert(tk.END, f"You: {user_text}\n")
        self.entry.delete(0, tk.END)

        # run agent in background thread so UI doesn't freeze
        threading.Thread(
            target=run_agent,
            args=(user_text, self.display_reply),
            daemon=True
        ).start()

    def display_reply(self, reply):
        self.chat_log.insert(tk.END, f"Bot: {reply}\n")


root = tk.Tk()
app = ChatUI(root)
root.mainloop()
