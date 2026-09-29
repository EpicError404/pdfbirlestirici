import os
import io
import threading
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF

# CustomTkinter genel ayarları
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class PDFMergerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Özgün PDF Birleştirici (Sıkıştırma Özellikli)")
        self.geometry("980x700")
        self.minsize(850, 550)

        self.create_widgets()

    def create_widgets(self):
        # ================== 1. ÜST ARAÇ ÇUBUĞU ==================
        self.toolbar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.toolbar_frame.pack(fill="x", padx=15, pady=10)

        self.btn_add_file = ctk.CTkButton(self.toolbar_frame, text="➕ Dosya Ekle", command=self.add_files)
        self.btn_add_file.pack(side="left", padx=5)

        self.btn_add_folder = ctk.CTkButton(self.toolbar_frame, text="📁 Klasör Ekle", command=self.add_folder)
        self.btn_add_folder.pack(side="left", padx=5)

        self.btn_clear = ctk.CTkButton(self.toolbar_frame, text="🗑️ Tümünü Temizle", command=self.clear_all, fg_color="#C62828", hover_color="#B71C1C")
        self.btn_clear.pack(side="right", padx=5)

        # ================== 2. VE 3. MERKEZ & SAĞ PANEL ==================
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=5)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#2b2b2b", foreground="white", rowheight=30, fieldbackground="#2b2b2b", borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])
        style.configure("Treeview.Heading", background="#1f538d", foreground="white", font=('Arial', 10, 'bold'))

        self.tree_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.tree_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        columns = ("dosya_adi", "sayfa_sayisi", "sayfa_secimi", "dosya_yolu")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("dosya_adi", text="Dosya Adı")
        self.tree.heading("sayfa_sayisi", text="Sayfa Sayısı")
        self.tree.heading("sayfa_secimi", text="Sayfa Seçimi (Çift Tıkla)")
        self.tree.heading("dosya_yolu", text="Dosya Yolu")

        self.tree.column("dosya_adi", width=250)
        self.tree.column("sayfa_sayisi", width=100, anchor="center")
        self.tree.column("sayfa_secimi", width=180, anchor="center")
        self.tree.column("dosya_yolu", width=250)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.edit_page_selection)

        # Sağ Panel (Sıralama Butonları)
        self.right_panel = ctk.CTkFrame(self.main_frame, width=150, fg_color="transparent")
        self.right_panel.pack(side="right", fill="y", padx=5, pady=10)

        self.btn_up = ctk.CTkButton(self.right_panel, text="⬆️ Yukarı Taşı", command=self.move_up)
        self.btn_up.pack(pady=10)

        self.btn_down = ctk.CTkButton(self.right_panel, text="⬇️ Aşağı Taşı", command=self.move_down)
        self.btn_down.pack(pady=10)

        self.btn_remove = ctk.CTkButton(self.right_panel, text="❌ Seçileni Kaldır", command=self.remove_selected, fg_color="#555555")
        self.btn_remove.pack(pady=10)

        # ================== 4. ALT PANEL (ÇIKTI & İŞLEM) ==================
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.pack(fill="x", padx=15, pady=15)

        # Çıktı Konumu ve Adı
        self.output_dir = ctk.StringVar()
        ctk.CTkLabel(self.bottom_frame, text="Çıktı Klasörü:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_out_dir = ctk.CTkEntry(self.bottom_frame, textvariable=self.output_dir, width=400, state="readonly")
        self.entry_out_dir.grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(self.bottom_frame, text="Gözat...", width=80, command=self.browse_output).grid(row=0, column=2, padx=10, pady=5)

        self.output_name = ctk.StringVar(value="birlestirilmis_dosya.pdf")
        ctk.CTkLabel(self.bottom_frame, text="Çıktı Adı:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(self.bottom_frame, textvariable=self.output_name, width=400).grid(row=1, column=1, padx=10, pady=5)

        # Gelişmiş Seçenekler (Grid Yapısı)
        self.options_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.options_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="w")
        
        # 1. Satır: Boş Sayfa
        self.add_blank_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.options_frame, text="Dosyalar arasına boş sayfa ekle", variable=self.add_blank_var).grid(row=0, column=0, pady=5, sticky="w")
        
        # 2. Satır: Şifreleme
        self.encrypt_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.options_frame, text="Şifrele", variable=self.encrypt_var, command=self.toggle_password).grid(row=1, column=0, pady=5, sticky="w")
        self.password_entry = ctk.CTkEntry(self.options_frame, width=150, placeholder_text="Parola Girin", show="*")
        
        # 3. Satır: Sıkıştırma
        self.compress_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.options_frame, text="Çıktıyı Sıkıştır", variable=self.compress_var, command=self.toggle_compression).grid(row=2, column=0, pady=5, sticky="w")
        self.compress_level = ctk.CTkComboBox(self.options_frame, values=["Hafif", "Orta", "Yüksek"], state="disabled", width=150)
        self.compress_level.set("Orta")
        
        # İlerleme ve Ana Buton
        self.progress_bar = ctk.CTkProgressBar(self.bottom_frame, mode="determinate")
        self.progress_bar.grid(row=3, column=0, columnspan=2, padx=10, pady=15, sticky="ew")
        self.progress_bar.set(0)

        self.btn_merge = ctk.CTkButton(self.bottom_frame, text="🚀 PDF'leri Birleştir", height=45, fg_color="#2E7D32", hover_color="#1B5E20", command=self.start_merge_thread)
        self.btn_merge.grid(row=3, column=2, padx=10, pady=15)

    # --- UI Tetikleyicileri ---
    def toggle_password(self):
        if self.encrypt_var.get():
            self.password_entry.grid(row=1, column=1, padx=15, pady=5)
        else:
            self.password_entry.grid_forget()

    def toggle_compression(self):
        if self.compress_var.get():
            self.compress_level.configure(state="normal")
            self.compress_level.grid(row=2, column=1, padx=15, pady=5)
        else:
            self.compress_level.configure(state="disabled")
            self.compress_level.grid_forget()

    # --- Dosya İşlemleri ---
    def get_pdf_pages(self, file_path):
        try:
            reader = PdfReader(file_path)
            return len(reader.pages)
        except Exception:
            return "?"

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF Dosyaları", "*.pdf")])
        for f in files:
            self.tree.insert("", "end", values=(os.path.basename(f), self.get_pdf_pages(f), "Tümü", f))

    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            for file in os.listdir(folder):
                if file.lower().endswith(".pdf"):
                    f_path = os.path.join(folder, file)
                    self.tree.insert("", "end", values=(file, self.get_pdf_pages(f_path), "Tümü", f_path))

    def remove_selected(self):
        for item in self.tree.selection(): self.tree.delete(item)

    def clear_all(self):
        for item in self.tree.get_children(): self.tree.delete(item)

    def move_up(self):
        for item in self.tree.selection():
            idx = self.tree.index(item)
            if idx > 0: self.tree.move(item, self.tree.parent(item), idx - 1)

    def move_down(self):
        items = self.tree.selection()
        for item in reversed(items):
            idx = self.tree.index(item)
            if idx < len(self.tree.get_children()) - 1:
                self.tree.move(item, self.tree.parent(item), idx + 1)

    def edit_page_selection(self, event):
        selected = self.tree.selection()
        if not selected: return
        item = selected[0]
        current_val = self.tree.item(item, "values")[2]
        new_val = simpledialog.askstring("Sayfa Seçimi", "Örn: 1-3, 5\n(Tüm sayfalar için 'Tümü' yazın)", initialvalue=current_val)
        if new_val:
            vals = list(self.tree.item(item, "values"))
            vals[2] = new_val
            self.tree.item(item, values=vals)

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder: self.output_dir.set(folder)

    # --- Birleştirme ve Sıkıştırma Mantığı ---
    def parse_page_string(self, page_str, max_pages):
        if page_str.lower() == "tümü" or not page_str.strip():
            return list(range(max_pages))
        
        pages = set()
        for part in page_str.replace(" ", "").split(","):
            if "-" in part:
                try:
                    s, e = map(int, part.split("-"))
                    pages.update(range(s - 1, e))
                except ValueError: pass
            else:
                try: pages.add(int(part) - 1)
                except ValueError: pass
        return sorted([p for p in pages if 0 <= p < max_pages])

    def start_merge_thread(self):
        items = self.tree.get_children()
        if not items:
            messagebox.showwarning("Uyarı", "PDF dosyaları ekleyin.")
            return
        if not self.output_dir.get() or not self.output_name.get():
            messagebox.showwarning("Uyarı", "Çıktı klasörü ve dosya adı belirleyin.")
            return

        self.btn_merge.configure(state="disabled", text="⏳ İşlem Yapılıyor...")
        self.progress_bar.set(0)
        threading.Thread(target=self.merge_pdfs_task, args=(items,), daemon=True).start()

    def merge_pdfs_task(self, items):
        writer = PdfWriter()
        total = len(items)
        
        try:
            # 1. AŞAMA: Birleştirme (pypdf)
            for index, item in enumerate(items):
                vals = self.tree.item(item, "values")
                reader = PdfReader(vals[3])
                pages_to_add = self.parse_page_string(vals[2], len(reader.pages))
                
                for p_num in pages_to_add:
                    writer.add_page(reader.pages[p_num])
                
                if self.add_blank_var.get() and index < total - 1:
                    writer.add_blank_page()
                
                self.progress_bar.set(((index + 1) / total) * 0.7) # İlerlemenin %70'i birleştirme

            out_path = os.path.join(self.output_dir.get(), self.output_name.get())
            if not out_path.lower().endswith(".pdf"): out_path += ".pdf"
            pwd = self.password_entry.get() if self.encrypt_var.get() else None

            # 2. AŞAMA: Sıkıştırma ve Kaydetme (PyMuPDF)
            if self.compress_var.get():
                self.after(0, lambda: self.btn_merge.configure(text="🗜️ Sıkıştırılıyor... (Lütfen Bekleyin)"))
                
                # Dosyayı önce RAM'e (BytesIO) yazıyoruz
                temp_buffer = io.BytesIO()
                writer.write(temp_buffer)
                temp_buffer.seek(0)
                
                # PyMuPDF ile RAM'deki dosyayı okuyoruz
                doc = fitz.open(stream=temp_buffer, filetype="pdf")
                
                # Sıkıştırma Seviyesi Parametreleri (Garbage Collection & Deflate)
                lvl = self.compress_level.get()
                save_kwargs = {"deflate": True}
                
                if lvl == "Hafif": save_kwargs["garbage"] = 2
                elif lvl == "Orta": save_kwargs["garbage"] = 3
                elif lvl == "Yüksek": save_kwargs["garbage"] = 4
                
                # Şifreleme (PyMuPDF üzerinden)
                if pwd:
                    save_kwargs["encryption"] = fitz.PDF_ENCRYPT_AES_256
                    save_kwargs["owner_pw"] = pwd
                    save_kwargs["user_pw"] = pwd
                    
                doc.save(out_path, **save_kwargs)
                doc.close()
                temp_buffer.close()
                self.progress_bar.set(1.0)
                
            else:
                # Sıkıştırma Yoksa Sadece Pypdf ile Şifrele ve Kaydet
                if pwd: writer.encrypt(pwd)
                with open(out_path, "wb") as f_out:
                    writer.write(f_out)
                self.progress_bar.set(1.0)
                
            # İşlem bitimi
            original_size = sum(os.path.getsize(self.tree.item(i, "values")[3]) for i in items) / (1024*1024)
            new_size = os.path.getsize(out_path) / (1024*1024)
            
            msg = f"Başarılı! Dosya kaydedildi:\n{out_path}\n\nYeni Boyut: {new_size:.2f} MB"
            if self.compress_var.get():
                msg += f"\n(Yaklaşık Orijinal Toplam: {original_size:.2f} MB)"
                
            self.after(0, lambda: messagebox.showinfo("Tamamlandı", msg))
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Hata", f"İşlem sırasında hata oluştu:\n{str(e)}"))
            
        finally:
            self.after(0, lambda: self.btn_merge.configure(state="normal", text="🚀 PDF'leri Birleştir"))
            self.after(0, lambda: self.progress_bar.set(0))

if __name__ == "__main__":
    app = PDFMergerApp()
    app.mainloop()