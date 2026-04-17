import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import threading
import subprocess
import sys
import os

from src.agents.agent import run
from src.tools.vlm import DEFAULT_MODEL, MODELS


# ─────────────────────────────────────────────────────────────
# Color Palette
# ─────────────────────────────────────────────────────────────
WINDOW_BG             = "#ECECEC"
PANEL_BG              = "#FFFFFF"
SEPARATOR             = "#D0D0D0"

TEXT_PRIMARY          = "#1C1C1C"
TEXT_SECONDARY        = "#6E6E6E"

BUTTON_UTILITY_BG     = "#FFFFFF"
BUTTON_UTILITY_BORDER = "#C8C8C8"
BUTTON_UTILITY_HOVER  = "#E5E5E5"

BUTTON_PRIMARY_BG     = "#0A84FF"
BUTTON_PRIMARY_HOVER  = "#006FE0"
BUTTON_PRIMARY_ACTIVE = "#006FE0"

COLOR_SUCCESS         = "#34C759"

LOG_BG                = "#1E1E1E"
LOG_TEXT              = "#E0E0E0"
# ─────────────────────────────────────────────────────────────


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
        self.root.title("PlainText")
        self.root.geometry("720x560")
        self.root.configure(bg=WINDOW_BG)
        self.root.resizable(True, True)

        self.log_visible = False
        self._bar_current = 0
        self._bar_total = 1
        self._bar_color = BUTTON_PRIMARY_BG
        self.open_button = None

        self._configure_grid()
        self._set_icon()
        self._build_ui()

    def _set_icon(self):
        try:
            icon = tk.PhotoImage(file="icon.png")
            self.root.iconphoto(True, icon)
        except Exception:
            pass

    # ─────────────────────────────────────────────────────────
    # Window Grid
    # row 0: title
    # row 1: subtitle
    # row 2: input panel
    # row 3: run button
    # row 4: open button (hidden until done)
    # row 5: progress panel
    # row 6: log toggle
    # row 7: log panel
    # ─────────────────────────────────────────────────────────
    def _configure_grid(self):
        self.root.columnconfigure(0, weight=1)
        for i in range(8):
            self.root.rowconfigure(i, weight=0)
        self.root.rowconfigure(7, weight=1)

    # ─────────────────────────────────────────────────────────
    # Hover helper
    # ─────────────────────────────────────────────────────────
    def add_hover(self, widget, normal, hover):
        widget.bind("<Enter>", lambda e: widget.config(bg=hover))
        widget.bind("<Leave>", lambda e: widget.config(bg=normal))

    # ─────────────────────────────────────────────────────────
    # Rounded panel helper
    # ─────────────────────────────────────────────────────────
    def rounded_panel(self, parent):
        frame = tk.Frame(
            parent,
            bg=PANEL_BG,
            highlightthickness=1,
            highlightbackground=SEPARATOR,
            bd=0
        )
        frame.pack_propagate(False)
        return frame

    # ─────────────────────────────────────────────────────────
    # Build UI
    # ─────────────────────────────────────────────────────────
    def _build_ui(self):

        # Title
        tk.Label(
            self.root, text="PlainText",
            font=("Helvetica", 20, "bold"),
            bg=WINDOW_BG, fg=TEXT_PRIMARY
        ).grid(row=0, column=0, pady=(18, 2))

        tk.Label(
            self.root, text="Convert complex documents to clean plain text",
            font=("Helvetica", 11),
            bg=WINDOW_BG, fg=TEXT_SECONDARY
        ).grid(row=1, column=0, pady=(0, 14))

        # Input Panel
        panel = self.rounded_panel(self.root)
        panel.grid(row=2, column=0, sticky="ew", padx=20)
        panel.columnconfigure(0, weight=1)

        # File selection
        tk.Label(panel, text="File", font=("Helvetica", 10, "bold"),
                 bg=PANEL_BG, fg=TEXT_SECONDARY).grid(row=0, column=0, sticky="w", pady=(12, 0), padx=16)

        self.pdf_path_var = tk.StringVar()
        tk.Entry(panel, textvariable=self.pdf_path_var, bd=0, relief="flat",
                 highlightthickness=1, highlightbackground=BUTTON_UTILITY_BORDER
                 ).grid(row=1, column=0, sticky="ew", padx=16, pady=4, ipady=4)

        btn_pdf = tk.Label(panel, text="Browse", bg=BUTTON_UTILITY_BG, fg=TEXT_PRIMARY,
                           bd=1, relief="solid", highlightbackground=BUTTON_UTILITY_BORDER,
                           highlightthickness=1, padx=12, pady=4, cursor="hand2")
        btn_pdf.grid(row=1, column=1, padx=(6, 16))
        btn_pdf.bind("<Button-1>", lambda e: self._browse_pdf())
        self.add_hover(btn_pdf, BUTTON_UTILITY_BG, BUTTON_UTILITY_HOVER)

        # Output selection
        tk.Label(panel, text="Output File", font=("Helvetica", 10, "bold"),
                 bg=PANEL_BG, fg=TEXT_SECONDARY).grid(row=2, column=0, sticky="w", pady=(10, 0), padx=16)

        self.output_path_var = tk.StringVar()
        tk.Entry(panel, textvariable=self.output_path_var, bd=0, relief="flat",
                 highlightthickness=1, highlightbackground=BUTTON_UTILITY_BORDER
                 ).grid(row=3, column=0, sticky="ew", padx=16, pady=4, ipady=4)

        btn_out = tk.Label(panel, text="Browse", bg=BUTTON_UTILITY_BG, fg=TEXT_PRIMARY,
                           bd=1, relief="solid", highlightbackground=BUTTON_UTILITY_BORDER,
                           highlightthickness=1, padx=12, pady=4, cursor="hand2")
        btn_out.grid(row=3, column=1, padx=(6, 16))
        btn_out.bind("<Button-1>", lambda e: self._browse_output())
        self.add_hover(btn_out, BUTTON_UTILITY_BG, BUTTON_UTILITY_HOVER)

        # Model selection
        tk.Label(panel, text="Model", font=("Helvetica", 10, "bold"),
                 bg=PANEL_BG, fg=TEXT_SECONDARY).grid(row=4, column=0, sticky="w", pady=(10, 0), padx=16)

        self.model_var = tk.StringVar(value=DEFAULT_MODEL)
        ttk.Combobox(panel, textvariable=self.model_var, values=MODELS, state="readonly"
                     ).grid(row=5, column=0, sticky="w", padx=16, pady=(4, 12))

        # Run Button (row 3)
        self.run_button = tk.Label(
            self.root, text="Run",
            bg=BUTTON_PRIMARY_BG, fg="white",
            font=("Helvetica", 13, "bold"),
            padx=24, pady=10, cursor="hand2"
        )
        self.run_button.grid(row=3, column=0, pady=(16, 4))
        self.run_button.bind("<Button-1>", lambda e: self._run())
        self.add_hover(self.run_button, BUTTON_PRIMARY_BG, BUTTON_PRIMARY_HOVER)

        # Open button placeholder (row 4) — empty label keeps row height stable
        self.open_button_placeholder = tk.Label(self.root, text="", bg=WINDOW_BG, height=1)
        self.open_button_placeholder.grid(row=4, column=0)

        # Progress Panel (row 5)
        progress_panel = self.rounded_panel(self.root)
        progress_panel.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 6))
        progress_panel.columnconfigure(0, weight=1)

        self.progress_label = tk.Label(
            progress_panel, text="", bg=PANEL_BG, fg=TEXT_SECONDARY,
            font=("Helvetica", 10)
        )
        self.progress_label.grid(row=0, column=0, sticky="w", padx=16, pady=(12, 0))

        self.progress_canvas = tk.Canvas(
            progress_panel, height=10, bg=SEPARATOR, highlightthickness=0
        )
        self.progress_canvas.grid(row=1, column=0, sticky="ew", padx=16, pady=(4, 12))
        self.progress_canvas.bind("<Configure>", lambda e: self._redraw_bar())

        # Log Toggle (row 6)
        self.log_toggle = tk.Label(
            self.root, text="▶ Show Log",
            font=("Helvetica", 10), bg=WINDOW_BG, fg=TEXT_SECONDARY, cursor="hand2"
        )
        self.log_toggle.grid(row=6, column=0, sticky="w", padx=20)
        self.log_toggle.bind("<Button-1>", lambda e: self._toggle_log())

        # Log Panel (row 7, hidden by default)
        self.log_frame = tk.Frame(self.root, bg=PANEL_BG)
        self.log_frame.grid(row=7, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.log_frame.grid_remove()
        self.log_frame.rowconfigure(0, weight=1)
        self.log_frame.columnconfigure(0, weight=1)

        self.log = scrolledtext.ScrolledText(
            self.log_frame, state="disabled", wrap="word",
            font=("Courier", 10), bg=LOG_BG, fg=LOG_TEXT,
            insertbackground=LOG_TEXT, relief="flat"
        )
        self.log.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

    # ─────────────────────────────────────────────────────────
    # Canvas Progress Bar
    # ─────────────────────────────────────────────────────────
    def _redraw_bar(self):
        self.progress_canvas.delete("all")
        w = self.progress_canvas.winfo_width()
        h = self.progress_canvas.winfo_height()
        filled = int(w * self._bar_current / max(self._bar_total, 1))
        if filled > 0:
            self.progress_canvas.create_rectangle(
                0, 0, filled, h, fill=self._bar_color, outline=""
            )

    # ─────────────────────────────────────────────────────────
    # Show / Hide Log
    # ─────────────────────────────────────────────────────────
    def _toggle_log(self):
        if self.log_visible:
            self.log_frame.grid_remove()
            self.log_toggle.config(text="▶ Show Log")
            self.log_visible = False
            self.root.geometry(self._collapsed_size)
        else:
            self._collapsed_size = self.root.geometry()  # save current size
            self.log_frame.grid()
            self.log_toggle.config(text="▼ Hide Log")
            self.log_visible = True

    # ─────────────────────────────────────────────────────────
    # File Browsing
    # ─────────────────────────────────────────────────────────
    def _browse_pdf(self):
        path = filedialog.askopenfilename(filetypes=[
            ("All supported files", "*.pdf *.png *.jpg *.jpeg *.tiff *.tif *.bmp *.webp"),
            ("PDF files", "*.pdf"),
            ("Image files", "*.png *.jpg *.jpeg *.tiff *.tif *.bmp *.webp"),
            ("All files", "*.*")
        ])
        if path:
            self.pdf_path_var.set(path)
            self.output_path_var.set(f"{os.path.splitext(path)[0]}_extracted.txt")

    def _browse_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text files", "*.txt")]
        )
        if path:
            self.output_path_var.set(path)

    # ─────────────────────────────────────────────────────────
    # Logging
    # ─────────────────────────────────────────────────────────
    def _log(self, message: str):
        self.root.after(0, self._log_main_thread, message)

    def _log_main_thread(self, message: str):
        self.log.configure(state="normal")
        self.log.insert("end", message + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    # ─────────────────────────────────────────────────────────
    # Progress
    # ─────────────────────────────────────────────────────────
    def _set_progress(self, current: int, total: int):
        self.root.after(0, self._set_progress_main_thread, current, total)

    def _set_progress_main_thread(self, current: int, total: int):
        self._bar_current = current
        self._bar_total = total
        self._bar_color = BUTTON_PRIMARY_BG
        self.progress_label.config(text=f"Processing page {current} of {total}…")
        self._redraw_bar()

    def _finish_bar(self, result: str):
        self._bar_current = self._bar_total
        self._bar_color = COLOR_SUCCESS
        self._redraw_bar()
        self.progress_label.config(text=f"✓ Done — saved to: {result}")
        self._show_open_button(result)

    # ─────────────────────────────────────────────────────────
    # Open File Button
    # ─────────────────────────────────────────────────────────
    def _show_open_button(self, path: str):
        if self.open_button is not None:
            self.open_button.destroy()
        self.open_button = tk.Label(
            self.root, text="Open Extracted Text File",
            bg=COLOR_SUCCESS, fg="white",
            font=("Helvetica", 11, "bold"),
            padx=20, pady=8, cursor="hand2"
        )
        self.open_button.grid(row=4, column=0, pady=(0, 4))
        self.open_button.bind("<Button-1>", lambda e: self._open_file(path))
        self.add_hover(self.open_button, COLOR_SUCCESS, "#2DB84D")

    def _open_file(self, path: str):
        subprocess.run(["open", path])

    # ─────────────────────────────────────────────────────────
    # Run Pipeline
    # ─────────────────────────────────────────────────────────
    def _run(self):
        pdf_path = self.pdf_path_var.get().strip()
        output_path = self.output_path_var.get().strip() or None
        model = self.model_var.get()

        if not pdf_path:
            self._log("Error: please select a file.")
            return

        # Hide open button if visible from previous run
        if self.open_button is not None:
            self.open_button.destroy()
            self.open_button = None

        self.run_button.configure(bg=BUTTON_PRIMARY_ACTIVE, text="Running…")
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
            if pdf_path.lower().endswith('.pdf'):
                total_pages = get_page_count(pdf_path)
            else:
                total_pages = 1
            self._set_progress(0, total_pages)

            import src.agents.agent as agent_module

            if hasattr(agent_module, 'process_page'):
                original_fn = agent_module.process_page
                attr_name = 'process_page'
            elif hasattr(agent_module, '_process_page'):
                original_fn = agent_module._process_page
                attr_name = '_process_page'
            else:
                original_fn = None
                attr_name = None

            current_page = [0]

            if attr_name:
                def tracked_process_page(image_path, model):
                    current_page[0] += 1
                    self._set_progress(current_page[0], total_pages)
                    return original_fn(image_path, model)

                setattr(agent_module, attr_name, tracked_process_page)

            result = run(pdf_path=pdf_path, output_path=output_path, model=model)

            if attr_name:
                setattr(agent_module, attr_name, original_fn)

            self._log(f"Done. Saved to: {result}")
            self.root.after(0, self._finish_bar, result)

        except Exception as e:
            self._log(f"Error: {e}")

        finally:
            sys.stdout = old_stdout
            self.root.after(0, self._reset_button)

    def _reset_button(self):
        self.run_button.configure(bg=BUTTON_PRIMARY_BG, text="Run")
        self.run_button.bind("<Button-1>", lambda e: self._run())
        self.add_hover(self.run_button, BUTTON_PRIMARY_BG, BUTTON_PRIMARY_HOVER)


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()

    style = ttk.Style()
    style.theme_use("default")

    style.configure(".", background=PANEL_BG)

    style.configure("TCombobox",
                    fieldbackground=PANEL_BG,
                    background=PANEL_BG,
                    bordercolor=BUTTON_UTILITY_BORDER,
                    lightcolor=PANEL_BG,
                    darkcolor=PANEL_BG,
                    arrowcolor=TEXT_SECONDARY)

    style.map("TCombobox",
              focusfill=[("readonly", PANEL_BG)],
              fieldbackground=[("readonly", PANEL_BG)],
              bordercolor=[("focus", BUTTON_UTILITY_BORDER)])

    app = App(root)
    root.mainloop()