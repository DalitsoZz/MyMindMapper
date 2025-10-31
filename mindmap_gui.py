import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import threading
import mindmap_to_pdf


def run_conversion(plantuml_text, output_path, status_label, progress):
    try:
        progress.start()
        mindmap_to_pdf.mindmap_to_pdf(plantuml_text, output_file=output_path)
        progress.stop()
        status_label.config(text=f"✅ PDF saved: {output_path}", fg="#388E3C")
    except Exception as e:
        progress.stop()
        status_label.config(text=f"❌ Error: {e}", fg="#D32F2F")


def save_pdf():
    plantuml_text = text_box.get("1.0", tk.END).strip()
    if not plantuml_text:
        messagebox.showerror("Error", "Please paste PlantUML mindmap text.")
        return
    output_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialdir=mindmap_to_pdf.BASE_DIR,
        title="Save PDF as..."
    )
    if not output_path:
        return
    status_label.config(text="Converting...", fg="#1976D2")
    threading.Thread(target=run_conversion, args=(plantuml_text, output_path, status_label, progress)).start()


# --- UI Setup ---
root = tk.Tk()
root.title("PlantUML Mindmap to PDF Converter")
root.geometry("800x600")
root.configure(bg="#F5F5F5")

title_label = tk.Label(root, text="PlantUML Mindmap → PDF", font=("Segoe UI", 20, "bold"), bg="#F5F5F5", fg="#512DA8")
title_label.pack(pady=(20, 10))

desc_label = tk.Label(root, text="Paste your PlantUML mindmap text below. Click 'Convert & Save as PDF' to export.", font=("Segoe UI", 12), bg="#F5F5F5", fg="#333")
desc_label.pack(pady=(0, 10))

frame = tk.Frame(root, bg="#F5F5F5")
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

text_box = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=18, font=("Consolas", 12), bg="#FAFAFA", fg="#222", borderwidth=2, relief="groove")
text_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

button_frame = tk.Frame(frame, bg="#F5F5F5")
button_frame.pack(fill=tk.X, pady=(0, 10))

save_btn = tk.Button(button_frame, text="Convert & Save as PDF", font=("Segoe UI", 12, "bold"), bg="#1976D2", fg="white", activebackground="#1565C0", activeforeground="white", relief="raised", command=save_pdf)
save_btn.pack(side=tk.LEFT, padx=(0, 10))

progress = ttk.Progressbar(button_frame, mode="indeterminate", length=200)
progress.pack(side=tk.LEFT, padx=(10, 0))

status_label = tk.Label(frame, text="", font=("Segoe UI", 11), bg="#F5F5F5", fg="#1976D2")
status_label.pack(anchor=tk.W, pady=(0, 5))

# Footer
base_dir_label = tk.Label(root, text=f"Using base dir: {mindmap_to_pdf.BASE_DIR}", font=("Segoe UI", 9), bg="#F5F5F5", fg="#666")
base_dir_label.pack(side=tk.BOTTOM, pady=(2,0))

footer = tk.Label(root, text="© 2025 MyMindMap | Powered by PlantUML & Batik", font=("Segoe UI", 10), bg="#F5F5F5", fg="#888")
footer.pack(side=tk.BOTTOM, pady=(0,8))

root.mainloop()
