import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
import threading
import sys
import os
from src.agents.agent import run
from src.tools.vlm import DEFAULT_MODEL, MODELS

# ── Theme ────────────────────────────────────────────────────────────────────
BG             = "#f5f5f5"   # app background
TEXT_PRIMARY   = "#212121"   # primary text
TEXT_SECONDARY = "#757575"   # secondary/muted text
BUTTON         = "#2196F3"   # run button
BUTTON_ACTIVE  = "#90CAF9"   # run button while processing
BUTTON_TEXT    = "white"     # run button text
LOG_BG         = "#212121"   # log background
LOG_TEXT       = "#e0e0e0"   # log text
# ─────────────────────────────────────────────────────────────────────────────

class StreamToLog:
    """Redirect stdout to the log widget in real time."""
    def __init__(self, log_func):
        self.log_func = log_func

    def write(self, message):
        if message.strip():
            self.log_func(message.strip())

    def flush(self):
        pass

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DePDF")
        self.root.geometry("720x560")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self._set_icon()
        self._build_ui()

    def _set_icon(self):
        icon = tk.PhotoImage(file="icon.png")
        self.root.iconphoto(True, icon)

    def _build_ui(self):
        # title
        tk.Label(
            self.root,
            text="DePDF",
            font=("Helvetica", 16, "bold"),
            bg=BG,
            fg=TEXT_PRIMARY
        ).pack(pady=(16, 4))

        tk.Label(
            self.root,
            text="Convert complex PDFs to clean plain text",
            font=("Helvetica", 10),
            bg=BG,
            fg=TEXT_SECONDARY
        ).pack(pady=(0, 12))

        # input frame
        input_frame = tk.Frame(self.root, bg=BG)
        input_frame.pack(fill="x", padx=20)

        # PDF selection
        tk.Label(input_frame, text="PDF File", font=("Helvetica", 10, "bold"), bg=BG).grid(row=0, column=0, sticky="w", pady=4)
        self.pdf_path_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.pdf_path_var, width=62, relief="solid").grid(row=1, column=0, sticky="ew", padx=(0, 6))
        tk.Button(input_frame, text="Browse", command=self._browse_pdf, relief="solid").grid(row=1, column=1)

        # output path
        tk.Label(input_frame, text="Output File", font=("Helvetica", 10, "bold"), bg=BG).grid(row=2, column=0, sticky="w", pady=(10, 4))
        self.output_path_var = tk.StringVar()
        tk.Entry(input_frame, textvariable=self.output_path_var, width=62, relief="solid").grid(row=3, column=0, sticky="ew", padx=(0, 6))
        tk.Button(input_frame, text="Browse", command=self._browse_output, relief="solid").grid(row=3, column=1)

        # model selection
        tk.Label(input_frame, text="Model", font=("Helvetica", 10, "bold"), bg=BG).grid(row=4, column=0, sticky="w", pady=(10, 4))
        self.model_var = tk.StringVar(value=DEFAULT_MODEL)
        ttk.Combobox(
            input_frame,
            textvariable=self.model_var,
            values=MODELS,
            state="readonly",
            width=24
        ).grid(row=5, column=0, sticky="w")

        # run button as Label for Mac color support
        self.run_button = tk.Label(
            self.root,
            text="Run",
            bg=BUTTON,
            fg=BUTTON_TEXT,
            font=("Helvetica", 11, "bold"),
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.run_button.pack(pady=14)
        self.run_button.bind("<Button-1>", lambda e: self._run())

        # progress bar
        progress_frame = tk.Frame(self.root, bg=BG)
        progress_frame.pack(fill="x", padx=20)

        self.progress_label = tk.Label(
            progress_frame,
            text="",
            font=("Helvetica", 9),
            bg=BG,
            fg=TEXT_SECONDARY
        )
        self.progress_label.pack(anchor="w")

        self.progress = ttk.Progressbar(progress_frame, mode="determinate", length=680)
        self.progress.pack(fill="x", pady=(2, 8))

        # log
        tk.Label(
            self.root,
            text="Log",
            font=("Helvetica", 10, "bold"),
            bg=BG
        ).pack(anchor="w", padx=20)

        self.log = scrolledtext.ScrolledText(
            self.root,
            height=10,
            state="disabled",
            wrap="word",
            font=("Courier", 10),
            bg=LOG_BG,
            fg=LOG_TEXT,
            insertbackground=BUTTON_TEXT,
            relief="flat"
        )
        self.log.pack(fill="both", expand=True, padx=20, pady=(4, 16))

    def _browse_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            self.pdf_path_var.set(path)
            base = os.path.splitext(path)[0]
            self.output_path_var.set(f"{base}_extracted.txt")

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if path:
            self.output_path_var.set(path)

    def _log(self, message: str):
        self.root.after(0, self._log_main_thread, message)

    def _log_main_thread(self, message: str):
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_progress(self, current: int, total: int):
        self.root.after(0, self._set_progress_main_thread, current, total)

    def _set_progress_main_thread(self, current: int, total: int):
        self.progress["maximum"] = total
        self.progress["value"] = current
        self.progress_label.config(text=f"Page {current} of {total}")

    def _run(self):
        pdf_path = self.pdf_path_var.get().strip()
        output_path = self.output_path_var.get().strip() or None
        model = self.model_var.get()

        if not pdf_path:
            self._log("Error: please select a PDF file.")
            return

        # disable button while processing
        self.run_button.configure(bg=BUTTON_ACTIVE, text="Running...")
        self.run_button.unbind("<Button-1>")

        threading.Thread(
            target=self._run_pipeline,
            args=(pdf_path, output_path, model),
            daemon=True
        ).start()

    def _run_pipeline(self, pdf_path: str, output_path: str, model: str):
        self._log(f"Starting: {os.path.basename(pdf_path)}")
        self._log(f"Model: {model}")

        old_stdout = sys.stdout
        sys.stdout = StreamToLog(self._log)

        try:
            from src.tools.pdf import get_page_count
            total_pages = get_page_count(pdf_path)
            self._set_progress(0, total_pages)

            import src.agents.agent as agent_module
            original_process_page = agent_module._process_page
            current_page = [0]

            def tracked_process_page(image_path, model):
                result = original_process_page(image_path, model)
                current_page[0] += 1
                self._set_progress(current_page[0], total_pages)
                return result

            agent_module._process_page = tracked_process_page

            result = run(pdf_path=pdf_path, output_path=output_path, model=model)

            agent_module._process_page = original_process_page

            self._log(f"Done. Saved to: {result}")

        except Exception as e:
            self._log(f"Error: {e}")

        finally:
            sys.stdout = old_stdout
            self.root.after(0, self._reset_button)

    def _reset_button(self):
        self.run_button.configure(bg=BUTTON, text="Run")
        self.run_button.bind("<Button-1>", lambda e: self._run())


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()