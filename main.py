import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os

class SpriteMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sprite Sheet Merger")
        self.root.geometry("1280x1024")
        
        # Data structure to hold loaded sprites
        self.sprites = [] # List of dicts: {path, rows, cols, scale}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Top Frame for "Add" and "Delete" buttons
        top_frame = tk.Frame(self.root, pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        
        btn_add = tk.Button(top_frame, text="Добавить спрайтшит", command=self.add_sprite, font=("Arial", 10, "bold"), bg="#4CAF50", fg="white", padx=10, pady=5)
        btn_add.pack(side=tk.LEFT, padx=20)
        
        btn_delete = tk.Button(top_frame, text="Удалить выбранный", command=self.delete_sprite, font=("Arial", 10), bg="#f44336", fg="white", padx=10, pady=5)
        btn_delete.pack(side=tk.LEFT, padx=10)
        
        # Middle Frame - Treeview
        mid_frame = tk.Frame(self.root)
        mid_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        style = ttk.Style()
        style.configure("Treeview", rowheight=30, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        
        columns = ("path", "rows", "cols", "scale")
        self.tree = ttk.Treeview(mid_frame, columns=columns, show="headings", height=15)
        self.tree.heading("path", text="Файл")
        self.tree.heading("rows", text="Строки")
        self.tree.heading("cols", text="Столбцы")
        self.tree.heading("scale", text="Масштаб")
        
        self.tree.column("path", width=700)
        self.tree.column("rows", width=100, anchor=tk.CENTER)
        self.tree.column("cols", width=100, anchor=tk.CENTER)
        self.tree.column("scale", width=100, anchor=tk.CENTER)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(mid_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bottom Frame - Output Parameters
        bottom_frame = tk.LabelFrame(self.root, text="Параметры выходного спрайтлиста", pady=20, padx=20, font=("Arial", 10, "bold"))
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=20)
        
        # Params Grid
        param_frame = tk.Frame(bottom_frame)
        param_frame.pack(side=tk.LEFT)
        
        tk.Label(param_frame, text="Ширина вых. кадра (px):", font=("Arial", 10)).grid(row=0, column=0, padx=5, sticky=tk.W)
        self.out_width_var = tk.IntVar(value=560)
        tk.Entry(param_frame, textvariable=self.out_width_var, width=10, font=("Arial", 10)).grid(row=0, column=1, padx=5)
        
        tk.Label(param_frame, text="Высота вых. кадра (px):", font=("Arial", 10)).grid(row=0, column=2, padx=15, sticky=tk.W)
        self.out_height_var = tk.IntVar(value=740)
        tk.Entry(param_frame, textvariable=self.out_height_var, width=10, font=("Arial", 10)).grid(row=0, column=3, padx=5)
        
        tk.Label(param_frame, text="Количество столбцов:", font=("Arial", 10)).grid(row=0, column=4, padx=15, sticky=tk.W)
        self.out_cols_var = tk.IntVar(value=16)
        tk.Entry(param_frame, textvariable=self.out_cols_var, width=10, font=("Arial", 10)).grid(row=0, column=5, padx=5)
        
        btn_save = tk.Button(bottom_frame, text="Сохранить", command=self.save_sprite, bg="#2196F3", fg="white", font=("Arial", 12, "bold"), padx=30, pady=10)
        btn_save.pack(side=tk.RIGHT, padx=20)
        
    def add_sprite(self):
        file_path = filedialog.askopenfilename(
            title="Выберите спрайтшит",
            filetypes=[("PNG Images", "*.png"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        self.open_add_dialog(file_path)
        
    def open_add_dialog(self, file_path):
        dlg = tk.Toplevel(self.root)
        dlg.title("Добавление спрайта и предпросмотр")
        dlg.geometry("1280x1024")
        dlg.grab_set() # Make modal
        
        # Center the dialog based on main root window
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 640
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 512
        dlg.geometry(f"+{x}+{y}")
        
        try:
            original_img = Image.open(file_path).convert("RGBA")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить изображение:\n{e}")
            dlg.destroy()
            return
            
        # Left Frame: Preview
        left_frame = tk.Frame(dlg)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_label = tk.Label(left_frame, text="Размер кадра: 0x0 px", font=("Arial", 10, "bold"))
        info_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 5))
        
        # Navigation Frame
        nav_frame = tk.Frame(left_frame)
        nav_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        
        preview_state = {"current_frame": 0}
        
        def prev_frame():
            preview_state["current_frame"] = max(0, preview_state["current_frame"] - 1)
            update_preview(reset_frame=False)
            
        def next_frame():
            try:
                r = rows_var.get()
                c = cols_var.get()
                total = r * c
                preview_state["current_frame"] = min(total - 1, preview_state["current_frame"] + 1)
                update_preview(reset_frame=False)
            except:
                pass
                
        btn_prev = tk.Button(nav_frame, text="< Пред. кадр", command=prev_frame, font=("Arial", 9))
        btn_prev.pack(side=tk.LEFT, padx=(0, 10))
        
        btn_next = tk.Button(nav_frame, text="След. кадр >", command=next_frame, font=("Arial", 9))
        btn_next.pack(side=tk.LEFT)
        
        canvas_frame = tk.Frame(left_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Gray background to easily see transparency bounds
        canvas = tk.Canvas(canvas_frame, xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set, bg="#e0e0e0")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        h_scroll.config(command=canvas.xview)
        v_scroll.config(command=canvas.yview)
        
        # Right Frame: Settings
        right_frame = tk.Frame(dlg, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        tk.Label(right_frame, text="Параметры нарезки", font=("Arial", 12, "bold")).pack(pady=(0, 20))
        tk.Label(right_frame, text=f"Файл:\n{os.path.basename(file_path)}", font=("Arial", 10), justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 20))
        
        inputs_frame = tk.Frame(right_frame)
        inputs_frame.pack(fill=tk.X)
        
        tk.Label(inputs_frame, text="Кол-во строк:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=10, sticky=tk.W)
        rows_var = tk.IntVar(value=1)
        tk.Entry(inputs_frame, textvariable=rows_var, width=10, font=("Arial", 10)).grid(row=0, column=1, padx=5, pady=10)
        
        tk.Label(inputs_frame, text="Кол-во столбцов:", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=10, sticky=tk.W)
        cols_var = tk.IntVar(value=1)
        tk.Entry(inputs_frame, textvariable=cols_var, width=10, font=("Arial", 10)).grid(row=1, column=1, padx=5, pady=10)
        
        tk.Label(inputs_frame, text="Коэф. масштаба:", font=("Arial", 10)).grid(row=2, column=0, padx=5, pady=10, sticky=tk.W)
        scale_var = tk.DoubleVar(value=1.0)
        tk.Entry(inputs_frame, textvariable=scale_var, width=10, font=("Arial", 10)).grid(row=2, column=1, padx=5, pady=10)
        
        def update_preview(reset_frame=True):
            try:
                r = rows_var.get()
                c = cols_var.get()
                s = scale_var.get()
            except tk.TclError:
                if reset_frame:
                    messagebox.showerror("Ошибка", "Введите корректные числовые значения")
                return
                
            if r <= 0 or c <= 0 or s <= 0:
                if reset_frame:
                    messagebox.showerror("Ошибка", "Значения должны быть больше 0")
                return
                
            total = r * c
            if reset_frame or preview_state["current_frame"] >= total:
                preview_state["current_frame"] = 0
                
            frame_idx = preview_state["current_frame"]
            
            frame_w = original_img.width // c
            frame_h = original_img.height // r
            
            s_col = frame_idx % c
            s_row = frame_idx // c
            
            # Get the current frame
            frame_img = original_img.crop((s_col * frame_w, s_row * frame_h, (s_col + 1) * frame_w, (s_row + 1) * frame_h))
            
            # Scale frame
            if s != 1.0:
                new_size = (int(frame_w * s), int(frame_h * s))
                resample_filter = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
                frame_img = frame_img.resize(new_size, resample_filter)
                
            scaled_w = frame_img.width
            scaled_h = frame_img.height
            
            # Find useful image bounding box using alpha channel
            alpha = frame_img.split()[-1]
            bbox = alpha.getbbox()
            
            frame_title = f"Кадр {frame_idx + 1} (синий)"
            
            if bbox:
                useful_w = bbox[2] - bbox[0]
                useful_h = bbox[3] - bbox[1]
                info_text = f"Спрайтшит: {original_img.width}x{original_img.height} px | {frame_title}: {scaled_w}x{scaled_h} px | Спрайт (зелёный): {useful_w}x{useful_h} px"
            else:
                info_text = f"Спрайтшит: {original_img.width}x{original_img.height} px | {frame_title}: {scaled_w}x{scaled_h} px | Спрайт: пустой"
                
            info_label.config(text=info_text)
            
            # Update canvas
            photo = ImageTk.PhotoImage(frame_img)
            canvas.delete("all")
            canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            canvas.image = photo # Keep reference
            
            # Draw blue border around the whole frame
            canvas.create_rectangle(0, 0, scaled_w, scaled_h, outline="blue", width=2)
            
            if bbox:
                # Draw green rectangle (bbox = left, upper, right, lower)
                canvas.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3], outline="#00ff00", width=2)
                
            # Update scroll region
            canvas.config(scrollregion=(0, 0, scaled_w, scaled_h))
            
        btn_update = tk.Button(inputs_frame, text="Обновить превью", command=lambda: update_preview(reset_frame=True), bg="#FF9800", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5)
        btn_update.grid(row=3, column=0, columnspan=2, pady=15)
        
        # Initial preview call
        update_preview()
        
        def confirm():
            try:
                r = rows_var.get()
                c = cols_var.get()
                s = scale_var.get()
                if r <= 0 or c <= 0 or s <= 0:
                    raise ValueError("Значения должны быть больше 0")
                
                # Add to structure and treeview
                self.sprites.append({
                    "path": file_path,
                    "rows": r,
                    "cols": c,
                    "scale": s
                })
                self.tree.insert("", tk.END, values=(file_path, r, c, s))
                dlg.destroy()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Некорректные параметры: {e}")
                
        btn_confirm = tk.Button(right_frame, text="Добавить в список", command=confirm, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=20, pady=10)
        btn_confirm.pack(side=tk.BOTTOM, pady=20)
        
    def delete_sprite(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Внимание", "Выберите элемент для удаления")
            return
            
        for item in selected_items:
            index = self.tree.index(item)
            self.sprites.pop(index)
            self.tree.delete(item)

    def save_sprite(self):
        if not self.sprites:
            messagebox.showwarning("Внимание", "Список спрайтов пуст!")
            return
            
        try:
            out_w = self.out_width_var.get()
            out_h = self.out_height_var.get()
            out_cols = self.out_cols_var.get()
            
            if out_w <= 0 or out_h <= 0 or out_cols <= 0:
                raise ValueError("Размеры и количество столбцов должны быть больше 0")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректные параметры вывода: {e}")
            return
            
        save_path = filedialog.asksaveasfilename(
            title="Сохранить итоговый спрайтшит",
            defaultextension=".png",
            filetypes=[("PNG Images", "*.png")]
        )
        if not save_path:
            return
            
        try:
            num_rows = len(self.sprites)
            # Create a transparent RGBA image for the output
            result_img = Image.new("RGBA", (out_w * out_cols, out_h * num_rows), (0, 0, 0, 0))
            
            for row_idx, sprite_info in enumerate(self.sprites):
                try:
                    img = Image.open(sprite_info["path"]).convert("RGBA")
                except Exception as e:
                    messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить {sprite_info['path']}:\n{e}")
                    return

                src_rows = sprite_info["rows"]
                src_cols = sprite_info["cols"]
                scale = sprite_info["scale"]
                
                src_frame_w = img.width // src_cols
                src_frame_h = img.height // src_rows
                
                total_src_frames = src_rows * src_cols
                
                for col_idx in range(out_cols):
                    if col_idx < total_src_frames:
                        # Find the corresponding col and row in the source image
                        s_col = col_idx % src_cols
                        s_row = col_idx // src_cols
                        
                        box = (
                            s_col * src_frame_w,
                            s_row * src_frame_h,
                            (s_col + 1) * src_frame_w,
                            (s_row + 1) * src_frame_h
                        )
                        frame_img = img.crop(box)
                        
                        # Scale the frame if needed
                        if scale != 1.0:
                            new_size = (int(src_frame_w * scale), int(src_frame_h * scale))
                            resample_filter = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
                            frame_img = frame_img.resize(new_size, resample_filter)
                        
                        # Calculate center position in the output cell
                        pos_x = col_idx * out_w + (out_w - frame_img.width) // 2
                        pos_y = row_idx * out_h + (out_h - frame_img.height) // 2
                        
                        # Paste into result using the frame itself as a mask to preserve transparency
                        result_img.paste(frame_img, (pos_x, pos_y), frame_img)
                        
            result_img.save(save_path, "PNG")
            messagebox.showinfo("Успех", f"Спрайтшит успешно сохранен!\n\nРазмер файла: {result_img.width}x{result_img.height} px\nПуть: {save_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpriteMergerApp(root)
    root.mainloop()
