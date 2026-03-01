import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext
from PIL import Image, ImageTk

from chatAgent import create_graph, send_message, save_graph_image, AgentState

CONFIG = {"configurable": {"thread_id": "my-chat-session"}, "recursion_limit": 100}

# Colours
BG_MAIN    = "#252422"   
BG_TWO     = "#403d39"   
BG_INPUT   = "#59554f" 
BTN =   "#8d99ae"
TEXT_BTN = "#003049"
TEXT_GEN   = "#fdf0d5"  
TEXT_LABEL    = "#eae2b7" 
TEXT_USER    = "#06d6a0"   
TEXT_LLAVA   = "#ef476f" 
TEXT_SYST  = "#ffd166"  

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("LLaVA Chat Agent")
        self.root.geometry("950x650")
        self.root.configure(bg=BG_MAIN)

        self.graph = create_graph()  # build graph and save
        save_graph_image(self.graph)

        self.image_path: str = ""
        self.state: AgentState = {    # initial agent state
            "user_input": "",
            "should_exit": False,
            "llm_response": "",
            "messages": [],
        }

        self._build_ui()

    def _build_ui(self):

        left = tk.Frame(self.root, width=320, bg=BG_MAIN)   ### left pane for image
        left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left.pack_propagate(False)

        tk.Label(
            left, text="IMAGE", bg=BG_MAIN, fg=TEXT_LABEL,    # image pane label
            font=("Helvetica", 10, "bold")
        ).pack(anchor="w", pady=(0, 6))

        image_frame = tk.Frame(left, bg=BG_INPUT, height=380)
        image_frame.pack(fill=tk.X)
        image_frame.pack_propagate(False)

        self.image_label = tk.Label(
            image_frame, text="No image selected\n\nClick below to choose one",
            bg=BG_INPUT, fg=TEXT_LABEL, wraplength=280, justify=tk.CENTER
        )
        self.image_label.pack(expand=True)

        tk.Button(                                      # button to pick image
            left, text="📁 Choose Image", command=self._pick_image,
            bg=BTN, fg=TEXT_BTN, relief=tk.FLAT,
            padx=10, pady=6, cursor="hand2"
        ).pack(fill=tk.X, pady=(8, 0))

        right = tk.Frame(self.root, bg=BG_TWO)                           ### rigth pane for chat
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

        tk.Label(
            right, text="CHAT", bg=BG_TWO, fg=TEXT_LABEL,        # right pane label
            font=("Helvetica", 10, "bold")
        ).pack(anchor="w", padx=10, pady=(6, 0))

        self.chat_display = scrolledtext.ScrolledText(            # chat display
            right, state=tk.DISABLED, wrap=tk.WORD,
            bg=BG_TWO, fg=TEXT_GEN, font=("Helvetica", 12),
            relief=tk.FLAT, padx=10, pady=10,
            insertbackground=TEXT_GEN
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=6)

        self.chat_display.tag_config("user",      foreground=TEXT_USER,   font=("Helvetica", 12, "bold"))
        self.chat_display.tag_config("assistant", foreground=TEXT_LLAVA,  font=("Helvetica", 12))
        self.chat_display.tag_config("system",    foreground=TEXT_SYST, font=("Helvetica", 11, "italic"))

        input_row = tk.Frame(right, bg=BG_TWO)        # make space for input
        input_row.pack(fill=tk.X, padx=6, pady=8)

        self.input_box = tk.Entry(                       # input box
            input_row, bg=BG_INPUT, fg=TEXT_GEN,
            insertbackground=TEXT_GEN, font=("Helvetica", 12),
            relief=tk.FLAT
        )
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 6))
        self.input_box.bind("<Return>", lambda e: self._submit())

        self.send_btn = tk.Button(                             # input send button
            input_row, text="Send", command=self._submit,
            bg=BTN, fg=TEXT_BTN, relief=tk.FLAT,
            padx=14, pady=6, cursor="hand2"
        )
        self.send_btn.pack(side=tk.LEFT)

    def _pick_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not path:
            return

        self.image_path = path

        # Reset conversation when a new image is chosen
        self.state = {
            "user_input": "",
            "should_exit": False,
            "llm_response": "",
            "messages": [],
        }
        self._clear_chat()
        self._append("system", f"Image loaded: {path}")

        # Display thumbnail
        img = Image.open(path)
        img.thumbnail((300, 380))
        photo = ImageTk.PhotoImage(img)
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo  # keep reference to avoid GC

    def _clear_chat(self):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.configure(state=tk.DISABLED)

    def _append(self, role: str, text: str):
        self.chat_display.configure(state=tk.NORMAL)
        if role == "system":
            # System messages have no label, insert entirely in system colour
            self.chat_display.insert(tk.END, text + "\n\n", "system")
        else:
            prefix = {"user": "You: ", "assistant": "LLaVA: "}.get(role, "")
            # Label in colour, content in plain white
            self.chat_display.insert(tk.END, prefix, role)
            self.chat_display.insert(tk.END, text + "\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.configure(state=tk.DISABLED)

    def _submit(self):
        user_input = self.input_box.get().strip()
        if not user_input:
            return
        if not self.image_path:
            self._append("system", "Please select an image first.")
            return

        self.input_box.delete(0, tk.END)
        self.send_btn.configure(state=tk.DISABLED, text="Thinking...")
        self._append("user", user_input)

        # Run agent in background thread so UI stays responsive
        threading.Thread(target=self._run_agent, args=(user_input,), daemon=True).start()

    def _run_agent(self, user_input: str):
        try:
            self.state = send_message(
                self.graph, user_input, self.image_path, self.state, CONFIG
            )
            reply = self.state["llm_response"]
        except Exception as e:
            reply = f"[Error: {e}]"

        # Schedule UI update on main thread
        self.root.after(0, self._on_response, reply)

    def _on_response(self, reply: str):
        self._append("assistant", reply)
        self.send_btn.configure(state=tk.NORMAL, text="Send")
        self.input_box.focus()


if __name__ == "__main__":
    root = tk.Tk()
    root.iconphoto(True, ImageTk.PhotoImage(Image.open("imgs/icon.png")))
    App(root)
    root.mainloop()