import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import google.generativeai as genai
import threading
import os

class DevNoteTakerApp:
    def __init__(self, root):
        self.root = root
        # Added a version number so it looks like an evolving internal tool
        self.root.title("Automated Dev Note-Taker v1.2")
        self.root.geometry("950x750")
        
        # Simple styling tweaks to make it look a bit nicer than default Tkinter
        self.root.configure(bg="#f8f9fa", padx=15, pady=15)
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
            
        style.configure("TFrame", background="#f8f9fa")
        style.configure("TLabel", background="#f8f9fa", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#2c3e50")
        style.configure("TLabelframe", background="#f8f9fa")
        style.configure("TLabelframe.Label", background="#f8f9fa", font=("Segoe UI", 10, "bold"), foreground="#34495e")
        style.configure("Action.TButton", font=("Segoe UI", 10, "bold"), background="#3498db", foreground="white")
        style.map("Action.TButton", background=[("active", "#2980b9")])

        # Title Header
        header = ttk.Label(root, text="🚀 Dev Note-Taker & Code Summarizer", style="Header.TLabel")
        header.pack(anchor="w", pady=(0, 15))
        
        # API Key Section
        api_frame = ttk.Frame(root)
        api_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(api_frame, text="Gemini API Key:").pack(side="left")
        self.api_key_entry = ttk.Entry(api_frame, width=45, show="*")
        self.api_key_entry.pack(side="left", padx=10)
        
        # Auto-fill from env if available (saves time!)
        env_key = os.getenv("GEMINI_API_KEY", "")
        if env_key:
            self.api_key_entry.insert(0, env_key)
            
        # Analysis Type Dropdown (New Feature)
        ttk.Label(api_frame, text="  Mode:").pack(side="left")
        self.mode_var = tk.StringVar(value="Standard PR/Meeting Notes")
        self.mode_combo = ttk.Combobox(api_frame, textvariable=self.mode_var, state="readonly", width=30)
        self.mode_combo['values'] = (
            "Standard PR/Meeting Notes",
            "Security & Bug Audit",
            "Refactoring Suggestions",
            "Executive Summary (Short)"
        )
        self.mode_combo.pack(side="left", padx=10)
            
        # Main Content Layout
        paned_window = ttk.PanedWindow(root, orient="vertical")
        paned_window.pack(fill="both", expand=True)
        
        # Top Panel: Input
        input_frame = ttk.LabelFrame(paned_window, text="📝 Input: Paste raw notes, transcripts, or PR descriptions here")
        paned_window.add(input_frame, weight=1)
        
        self.text_input = scrolledtext.ScrolledText(input_frame, wrap="word", font=("Consolas", 10), bg="#ffffff")
        self.text_input.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Button Panel
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", pady=12)
        
        self.summarize_btn = ttk.Button(btn_frame, text="⚡ Generate Summary", style="Action.TButton", command=self.start_processing)
        self.summarize_btn.pack(side="left")
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to process.")
        self.status_label = ttk.Label(btn_frame, textvariable=self.status_var, foreground="#7f8c8d")
        self.status_label.pack(side="left", padx=15)
        
        # Export Buttons (New Features)
        self.save_btn = ttk.Button(btn_frame, text="💾 Save as Markdown", command=self.save_to_file, state="disabled")
        self.save_btn.pack(side="right", padx=(10, 0))
        
        self.copy_btn = ttk.Button(btn_frame, text="📋 Copy to Clipboard", command=self.copy_to_clipboard, state="disabled")
        self.copy_btn.pack(side="right")
        
        # Bottom Panel: Output
        output_frame = ttk.LabelFrame(paned_window, text="✨ Output: AI Generated Documentation")
        paned_window.add(output_frame, weight=2)
        
        self.text_output = scrolledtext.ScrolledText(output_frame, wrap="word", font=("Consolas", 10), bg="#fdfdfe")
        self.text_output.pack(fill="both", expand=True, padx=8, pady=8)

    def start_processing(self):
        api_key = self.api_key_entry.get().strip()
        input_text = self.text_input.get("1.0", tk.END).strip()
        
        if not api_key:
            messagebox.showwarning("Missing API Key", "Dude, you forgot the Gemini API Key at the top!")
            return
            
        if not input_text:
            messagebox.showwarning("Missing Input", "Paste some text first before clicking generate.")
            return
            
        # Update UI state
        self.summarize_btn.config(state="disabled")
        self.copy_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        
        mode = self.mode_var.get()
        self.status_var.set(f"Running '{mode}' analysis... hang tight.")
        self.text_output.delete("1.0", tk.END)
        
        genai.configure(api_key=api_key)
        
        # Threading prevents the UI from freezing while waiting for the API
        threading.Thread(target=self.process_with_ai, args=(input_text, mode), daemon=True).start()
        
    def process_with_ai(self, text_content, mode):
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            # Switch prompts based on what the user selected in the dropdown
            if mode == "Security & Bug Audit":
                prompt = f"Analyze this text/code for security vulnerabilities, edge cases, and bugs. Provide a markdown report prioritizing high-risk items.\n\nText:\n{text_content}"
            elif mode == "Refactoring Suggestions":
                prompt = f"Review this text/code and suggest clean code refactoring improvements. Focus on readability, performance, and DRY principles. Provide examples.\n\nText:\n{text_content}"
            elif mode == "Executive Summary (Short)":
                prompt = f"Give a very brief, 3-bullet-point executive summary of this text, followed by a 1-sentence conclusion.\n\nText:\n{text_content}"
            else:
                prompt = f"""
                You are a senior developer assistant. Analyze this pull request description or meeting transcript snippet.
                
                Format the output strictly like this:
                ### 📝 Documentation
                [Summary of context and changes]
                
                ### ✅ Action Items
                [List key action items as checkboxes]
                
                ### ⚠️ Technical Debt & Flags
                [Highlight any potential technical debt or code smells]
                
                Input text:
                {text_content}
                """
            
            response = model.generate_content(prompt)
            self.root.after(0, self.show_result, response.text)
            
        except Exception as e:
            self.root.after(0, self.show_error, str(e))
            
    def show_result(self, result_text):
        self.text_output.insert(tk.END, result_text)
        self.summarize_btn.config(state="normal")
        self.copy_btn.config(state="normal")
        self.save_btn.config(state="normal")
        self.status_var.set("Done! ✅")
        
    def show_error(self, error_msg):
        self.text_output.insert(tk.END, f"--- ERROR ---\n{error_msg}")
        self.summarize_btn.config(state="normal")
        self.status_var.set("Failed.")
        messagebox.showerror("API Error", "Something went wrong. Check your API key or internet connection.")

    def copy_to_clipboard(self):
        output = self.text_output.get("1.0", tk.END).strip()
        if output:
            self.root.clipboard_clear()
            self.root.clipboard_append(output)
            self.status_var.set("Copied to clipboard! 📋")
            
    def save_to_file(self):
        output = self.text_output.get("1.0", tk.END).strip()
        if not output:
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Generated Docs"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(output)
                self.status_var.set(f"Saved to {os.path.basename(file_path)} 💾")
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save file:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DevNoteTakerApp(root)
    root.mainloop()
