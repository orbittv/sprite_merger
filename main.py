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
        
        btn_edit = tk.Button(top_frame, text="Редактировать выбранный", command=self.edit_sprite, font=("Arial", 10), bg="#FF9800", fg="white", padx=10, pady=5)
        btn_edit.pack(side=tk.LEFT, padx=10)
        
        btn_sync = tk.Button(top_frame, text="Синхронизировать масштаб по 1-й строке", command=self.sync_scales, font=("Arial", 10, "bold"), bg="#9C27B0", fg="white", padx=10, pady=5)
        btn_sync.pack(side=tk.LEFT, padx=10)
        
        btn_manual_scale = tk.Button(top_frame, text="Подгонка scale", command=self.open_manual_scale_dialog, font=("Arial", 10, "bold"), bg="#E91E63", fg="white", padx=10, pady=5)
        btn_manual_scale.pack(side=tk.LEFT, padx=10)
        
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
        param_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        input_row = tk.Frame(param_frame)
        input_row.pack(anchor=tk.W)
        
        tk.Label(input_row, text="Ширина вых. кадра (px):", font=("Arial", 10)).grid(row=0, column=0, padx=5, sticky=tk.W)
        self.out_width_var = tk.IntVar(value=560)
        tk.Entry(input_row, textvariable=self.out_width_var, width=10, font=("Arial", 10)).grid(row=0, column=1, padx=5)
        
        tk.Label(input_row, text="Высота вых. кадра (px):", font=("Arial", 10)).grid(row=0, column=2, padx=15, sticky=tk.W)
        self.out_height_var = tk.IntVar(value=740)
        tk.Entry(input_row, textvariable=self.out_height_var, width=10, font=("Arial", 10)).grid(row=0, column=3, padx=5)
        
        tk.Label(input_row, text="Кол-во кадров в строке:", font=("Arial", 10)).grid(row=0, column=4, padx=15, sticky=tk.W)
        self.out_cols_var = tk.IntVar(value=16)
        tk.Entry(input_row, textvariable=self.out_cols_var, width=10, font=("Arial", 10)).grid(row=0, column=5, padx=5)
        
        self.canvas_size_label = tk.Label(param_frame, text="Итоговый размер холста нового спрайтшита: 0x0 px", font=("Arial", 10, "bold"), fg="#555")
        self.canvas_size_label.pack(anchor=tk.W, pady=(10, 0), padx=5)
        
        self.out_width_var.trace_add("write", self.update_canvas_size_label)
        self.out_height_var.trace_add("write", self.update_canvas_size_label)
        self.out_cols_var.trace_add("write", self.update_canvas_size_label)
        
        btn_save = tk.Button(bottom_frame, text="Сохранить", command=self.save_sprite, bg="#2196F3", fg="white", font=("Arial", 12, "bold"), padx=30, pady=10)
        btn_save.pack(side=tk.RIGHT, padx=20)
        
        btn_calc = tk.Button(bottom_frame, text="Вычислить", command=self.calc_output_params, bg="#00BCD4", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10)
        btn_calc.pack(side=tk.RIGHT, padx=5)
        
    def update_canvas_size_label(self, *args):
        try:
            w = self.out_width_var.get()
            h = self.out_height_var.get()
            cols = self.out_cols_var.get()
            rows = len(self.sprites)
            total_w = w * cols
            total_h = h * rows
            self.canvas_size_label.config(text=f"Итоговый размер холста нового спрайтшита: {total_w}x{total_h} px")
        except:
            self.canvas_size_label.config(text="Итоговый размер холста нового спрайтшита: Неизвестно")

    def add_sprite(self):
        file_path = filedialog.askopenfilename(
            title="Выберите спрайтшит",
            filetypes=[("PNG Images", "*.png"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        self.open_add_dialog(file_path)
        
    def open_add_dialog(self, file_path, edit_index=None, edit_item=None):
        dlg = tk.Toplevel(self.root)
        dlg.title("Редактирование спрайта" if edit_index is not None else "Добавление спрайта и предпросмотр")
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
        r_val = self.sprites[edit_index]["rows"] if edit_index is not None else 1
        rows_var = tk.IntVar(value=r_val)
        tk.Entry(inputs_frame, textvariable=rows_var, width=10, font=("Arial", 10)).grid(row=0, column=1, padx=5, pady=10)
        
        tk.Label(inputs_frame, text="Кол-во столбцов:", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=10, sticky=tk.W)
        c_val = self.sprites[edit_index]["cols"] if edit_index is not None else 1
        cols_var = tk.IntVar(value=c_val)
        tk.Entry(inputs_frame, textvariable=cols_var, width=10, font=("Arial", 10)).grid(row=1, column=1, padx=5, pady=10)
        
        tk.Label(inputs_frame, text="Коэф. масштаба:", font=("Arial", 10)).grid(row=2, column=0, padx=5, pady=10, sticky=tk.W)
        s_val = self.sprites[edit_index]["scale"] if edit_index is not None else 1.0
        scale_var = tk.DoubleVar(value=s_val)
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
        
        presets_frame = tk.Frame(inputs_frame)
        presets_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        def set_preset(n):
            rows_var.set(n)
            cols_var.set(n)
            update_preview(reset_frame=True)
            
        for i in range(1, 7):
            btn = tk.Button(presets_frame, text=f"{i}x{i}", font=("Arial", 9), width=3, bg="#E0E0E0", command=lambda n=i: set_preset(n))
            btn.pack(side=tk.LEFT, padx=2)
        
        # Initial preview call
        update_preview()
        
        def confirm():
            try:
                r = rows_var.get()
                c = cols_var.get()
                s = scale_var.get()
                if r <= 0 or c <= 0 or s <= 0:
                    raise ValueError("Значения должны быть больше 0")
                
                if edit_index is not None:
                    self.sprites[edit_index]["rows"] = r
                    self.sprites[edit_index]["cols"] = c
                    self.sprites[edit_index]["scale"] = s
                    self.tree.item(edit_item, values=(file_path, r, c, s))
                else:
                    self.sprites.append({
                        "path": file_path,
                        "rows": r,
                        "cols": c,
                        "scale": s
                    })
                    self.tree.insert("", tk.END, values=(file_path, r, c, s))
                dlg.destroy()
                self.update_canvas_size_label()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Некорректные параметры: {e}")
                
        btn_text = "Сохранить изменения" if edit_index is not None else "Добавить в список"
        btn_confirm = tk.Button(right_frame, text=btn_text, command=confirm, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=20, pady=10)
        btn_confirm.pack(side=tk.BOTTOM, pady=20)
        
    def edit_sprite(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Внимание", "Выберите элемент для редактирования")
            return
            
        if len(selected_items) > 1:
            messagebox.showwarning("Внимание", "Выберите только один элемент")
            return
            
        item = selected_items[0]
        index = self.tree.index(item)
        sprite_info = self.sprites[index]
        self.open_add_dialog(sprite_info["path"], edit_index=index, edit_item=item)

    def open_manual_scale_dialog(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Внимание", "Выберите элемент для подгонки")
            return
            
        selected_item = selected_items[0]
        selected_index = self.tree.index(selected_item)
        
        if selected_index == 0:
            messagebox.showwarning("Внимание", "Выбран первый элемент, он является эталоном. Выберите другой элемент из списка.")
            return
            
        if len(self.sprites) < 2:
            messagebox.showwarning("Внимание", "Для подгонки нужно как минимум два спрайтшита в списке.")
            return

        ref_sprite = self.sprites[0]
        tgt_sprite = self.sprites[selected_index]
        
        dlg = tk.Toplevel(self.root)
        dlg.title("Ручная подгонка scale")
        dlg.geometry("1280x1024")
        dlg.grab_set()
        
        # Center the dialog
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 640
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 512
        dlg.geometry(f"+{x}+{y}")
        
        # Layout
        top_frame = tk.Frame(dlg)
        top_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        
        ref_top = tk.Frame(top_frame, width=600, height=40)
        ref_top.pack_propagate(False)
        ref_top.pack(side=tk.LEFT, padx=10, expand=True)
        
        tgt_top = tk.Frame(top_frame, width=600, height=40)
        tgt_top.pack_propagate(False)
        tgt_top.pack(side=tk.RIGHT, padx=10, expand=True)

        dlg.ref_frame = 0
        dlg.tgt_frame = 0

        def change_ref_frame(delta):
            total = ref_sprite["rows"] * ref_sprite["cols"]
            dlg.ref_frame = (dlg.ref_frame + delta) % total
            render_sprite(cv_ref, ref_sprite, ref_sprite["scale"], is_ref=True, frame_idx=dlg.ref_frame)
            
        def change_tgt_frame(delta):
            total = tgt_sprite["rows"] * tgt_sprite["cols"]
            dlg.tgt_frame = (dlg.tgt_frame + delta) % total
            # We use scale_val.get() which is defined below, but evaluated lazily
            render_sprite(cv_tgt, tgt_sprite, scale_val.get(), is_ref=False, frame_idx=dlg.tgt_frame)

        tk.Button(ref_top, text="◀", font=("Arial", 14), command=lambda: change_ref_frame(-1)).pack(side=tk.LEFT, expand=True, anchor=tk.E, padx=10)
        tk.Button(ref_top, text="▶", font=("Arial", 14), command=lambda: change_ref_frame(1)).pack(side=tk.RIGHT, expand=True, anchor=tk.W, padx=10)
        
        tk.Button(tgt_top, text="◀", font=("Arial", 14), command=lambda: change_tgt_frame(-1)).pack(side=tk.LEFT, expand=True, anchor=tk.E, padx=10)
        tk.Button(tgt_top, text="▶", font=("Arial", 14), command=lambda: change_tgt_frame(1)).pack(side=tk.RIGHT, expand=True, anchor=tk.W, padx=10)
        
        canvas_frame = tk.Frame(dlg, bg="#222")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        cv_w, cv_h = 600, 800
        cv_ref = tk.Canvas(canvas_frame, width=cv_w, height=cv_h, bg="#333", relief=tk.SUNKEN, bd=2)
        cv_ref.pack(side=tk.LEFT, padx=10, pady=10, expand=True)
        
        cv_tgt = tk.Canvas(canvas_frame, width=cv_w, height=cv_h, bg="#333", relief=tk.SUNKEN, bd=2)
        cv_tgt.pack(side=tk.RIGHT, padx=10, pady=10, expand=True)
        
        def draw_grid_and_ruler(canvas):
            # Draw 10px dashed grid lines
            for i in range(0, cv_w, 10):
                canvas.create_line(i, 0, i, cv_h, fill="#4a4a4a", dash=(1, 3), tags="grid")
            for i in range(0, cv_h, 10):
                canvas.create_line(0, i, cv_w, i, fill="#4a4a4a", dash=(1, 3), tags="grid")
            
            # Draw rulers
            for i in range(0, cv_w, 50):
                if i > 0:
                    canvas.create_line(i, 0, i, 15, fill="#aaa", width=2, tags="ruler")
                    canvas.create_text(i, 22, text=str(i), fill="#ccc", font=("Arial", 8), tags="ruler")
            for i in range(0, cv_h, 50):
                if i > 0:
                    canvas.create_line(0, i, 15, i, fill="#aaa", width=2, tags="ruler")
                    canvas.create_text(25, i, text=str(i), fill="#ccc", font=("Arial", 8), tags="ruler")

        draw_grid_and_ruler(cv_ref)
        draw_grid_and_ruler(cv_tgt)
        
        # Draw floor line
        floor_y = cv_h - 20
        cv_ref.create_line(0, floor_y, cv_w, floor_y, fill="#00ff00", dash=(4, 4), tags="floor")
        cv_tgt.create_line(0, floor_y, cv_w, floor_y, fill="#00ff00", dash=(4, 4), tags="floor")
        
        # Draw center lines
        center_x = cv_w // 2
        center_y = cv_h // 2
        cv_ref.create_line(center_x, 0, center_x, cv_h, fill="red", dash=(4, 4), tags="center")
        cv_ref.create_line(0, center_y, cv_w, center_y, fill="red", dash=(4, 4), tags="center")
        cv_tgt.create_line(center_x, 0, center_x, cv_h, fill="red", dash=(4, 4), tags="center")
        cv_tgt.create_line(0, center_y, cv_w, center_y, fill="red", dash=(4, 4), tags="center")
        
        # Draggable Guides
        dlg.guides = {
            "h1": {"y": 200},
            "h2": {"y": 300},
            "h3": {"y": 400},
            "h4": {"y": 500},
            "v1": {"x": 200},
            "v2": {"x": 400}
        }
        
        def draw_guides():
            for c in (cv_ref, cv_tgt):
                c.delete("guide")
                
                # Horizontal guides
                for key in ["h1", "h2", "h3", "h4"]:
                    y = dlg.guides[key]["y"]
                    c.create_line(0, y, cv_w, y, fill="#00BFFF", width=2, tags=("guide", f"guide_{key}"))
                    num = key[1]
                    c.create_text(25, y - 10, text=num, fill="#00BFFF", font=("Arial", 10, "bold"), tags=("guide", f"guide_{key}"))
                
                # Vertical guides
                for key in ["v1", "v2"]:
                    x = dlg.guides[key]["x"]
                    c.create_line(x, 0, x, cv_h, fill="#00BFFF", width=2, tags=("guide", f"guide_{key}"))
                    num = key[1]
                    c.create_text(x - 10, 25, text=num, fill="#00BFFF", font=("Arial", 10, "bold"), tags=("guide", f"guide_{key}"))
                # Distances
                dist_h1_h2 = abs(dlg.guides["h2"]["y"] - dlg.guides["h1"]["y"])
                dist_v1_v2 = abs(dlg.guides["v2"]["x"] - dlg.guides["v1"]["x"])
                
                tl_x = min(dlg.guides["v1"]["x"], dlg.guides["v2"]["x"])
                
                # First box top-left
                tl_y1 = min(dlg.guides["h1"]["y"], dlg.guides["h2"]["y"])
                c.create_text(tl_x + 5, tl_y1 + 5, text=f"↔ {int(dist_v1_v2)}px", fill="#FF9800", font=("Arial", 10, "bold"), anchor=tk.NW, tags="guide")
                c.create_text(tl_x + 5, tl_y1 + 20, text=f"↕ {int(dist_h1_h2)}px", fill="#FF9800", font=("Arial", 10, "bold"), anchor=tk.NW, tags="guide")

                # Second box top-left
                dist_h3_h4 = abs(dlg.guides["h4"]["y"] - dlg.guides["h3"]["y"])
                tl_y2 = min(dlg.guides["h3"]["y"], dlg.guides["h4"]["y"])
                c.create_text(tl_x + 5, tl_y2 + 5, text=f"↔ {int(dist_v1_v2)}px", fill="#FF9800", font=("Arial", 10, "bold"), anchor=tk.NW, tags="guide")
                c.create_text(tl_x + 5, tl_y2 + 20, text=f"↕ {int(dist_h3_h4)}px", fill="#FF9800", font=("Arial", 10, "bold"), anchor=tk.NW, tags="guide")
                
        draw_guides()
        
        dlg.active_guide = None
        
        def on_guide_press(event, canvas):
            item = canvas.find_withtag("current")
            if item:
                tags = canvas.gettags(item[0])
                for t in tags:
                    if t.startswith("guide_"):
                        dlg.active_guide = t
                        break

        def on_guide_drag(event, canvas):
            if dlg.active_guide:
                guide_key = dlg.active_guide[6:]
                if guide_key == "h4":
                    return # h4 is not manually draggable
                    
                if guide_key.startswith("h"):
                    dlg.guides[guide_key]["y"] = max(0, min(cv_h, event.y))
                    # Update h4: distance between h3 and h4 equals distance between h1 and h2
                    dlg.guides["h4"]["y"] = dlg.guides["h3"]["y"] + (dlg.guides["h2"]["y"] - dlg.guides["h1"]["y"])
                elif guide_key.startswith("v"):
                    dlg.guides[guide_key]["x"] = max(0, min(cv_w, event.x))
                draw_guides()
                
        def on_guide_release(event):
            dlg.active_guide = None

        for c in (cv_ref, cv_tgt):
            c.tag_bind("guide", "<ButtonPress-1>", lambda e, can=c: on_guide_press(e, can))
            c.bind("<B1-Motion>", lambda e, can=c: on_guide_drag(e, can))
            c.bind("<ButtonRelease-1>", lambda e: on_guide_release(e))
            for key in ["h1", "h2", "h3"]:
                c.tag_bind(f"guide_{key}", "<Enter>", lambda e, can=c: can.config(cursor="sb_v_double_arrow"))
                c.tag_bind(f"guide_{key}", "<Leave>", lambda e, can=c: can.config(cursor=""))
            for key in ["v1", "v2"]:
                c.tag_bind(f"guide_{key}", "<Enter>", lambda e, can=c: can.config(cursor="sb_h_double_arrow"))
                c.tag_bind(f"guide_{key}", "<Leave>", lambda e, can=c: can.config(cursor=""))
        
        
        # Labels on canvas (handled inside render_sprite now)
        
        # Store photo images to prevent garbage collection
        dlg.photo_ref = None
        dlg.photo_tgt = None
        
        def render_sprite(canvas, sprite_info, current_scale, is_ref=False, frame_idx=0):
            try:
                img = Image.open(sprite_info["path"]).convert("RGBA")
            except Exception:
                return
                
            r = sprite_info["rows"]
            c = sprite_info["cols"]
            
            src_frame_w = img.width // c
            src_frame_h = img.height // r
            
            # Crop specific frame
            s_col = frame_idx % c
            s_row = frame_idx // c
            frame_img = img.crop((s_col * src_frame_w, s_row * src_frame_h, (s_col + 1) * src_frame_w, (s_row + 1) * src_frame_h))
            
            # Scale
            if current_scale != 1.0:
                new_size = (int(src_frame_w * current_scale), int(src_frame_h * current_scale))
                resample_filter = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
                frame_img = frame_img.resize(new_size, resample_filter)
                
            alpha = frame_img.split()[-1]
            bbox = alpha.getbbox()
            
            # Clear old image and label
            canvas.delete("sprite")
            tag_label = "ref_label" if is_ref else "tgt_label"
            canvas.delete(tag_label)
            
            if bbox:
                bbox_w = bbox[2] - bbox[0]
                pos_x = cv_w // 2 - bbox_w // 2 - bbox[0]
                pos_y = (cv_h - 20) - bbox[3]
                
                disp_img = Image.new("RGBA", (cv_w, cv_h), (0, 0, 0, 0))
                disp_img.paste(frame_img, (pos_x, pos_y), frame_img)
                
                photo = ImageTk.PhotoImage(disp_img)
                
                if is_ref:
                    dlg.photo_ref = photo
                    canvas.create_image(0, 0, image=dlg.photo_ref, anchor=tk.NW, tags="sprite")
                    canvas.create_text(cv_w // 2, 45, text=f"Эталон: кадр {frame_idx + 1} (Scale: {current_scale:.3f})", fill="white", font=("Arial", 14, "bold"), tags="ref_label")
                else:
                    dlg.photo_tgt = photo
                    canvas.create_image(0, 0, image=dlg.photo_tgt, anchor=tk.NW, tags="sprite")
                    canvas.create_text(cv_w // 2, 45, text=f"Настраиваемый: кадр {frame_idx + 1} (Scale: {current_scale:.3f})", fill="white", font=("Arial", 14, "bold"), tags="tgt_label")
                    
                canvas.tag_lower("sprite")
            else:
                prefix = "Эталон:" if is_ref else "Настраиваемый:"
                canvas.create_text(cv_w // 2, 45, text=f"{prefix} Пустой кадр {frame_idx + 1} (Scale: {current_scale:.3f})", fill="red", font=("Arial", 14, "bold"), tags=tag_label)
                    
        # Render reference once
        render_sprite(cv_ref, ref_sprite, ref_sprite["scale"], is_ref=True, frame_idx=dlg.ref_frame)
        
        # Bottom controls
        bottom_frame = tk.Frame(dlg, pady=20)
        bottom_frame.pack(fill=tk.X)
        
        tk.Label(bottom_frame, text="Scale:", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=(50, 10))
        
        scale_val = tk.DoubleVar(value=tgt_sprite["scale"])
        
        def on_scale_change(val):
            s = float(val)
            render_sprite(cv_tgt, tgt_sprite, s, is_ref=False, frame_idx=dlg.tgt_frame)
            
        scale_slider = tk.Scale(bottom_frame, variable=scale_val, from_=0.1, to=2.0, resolution=0.01, orient=tk.HORIZONTAL, length=400, command=on_scale_change)
        scale_slider.pack(side=tk.LEFT)
        
        def save_scale():
            new_s = scale_val.get()
            self.sprites[selected_index]["scale"] = new_s
            # Update treeview
            file_path = tgt_sprite["path"]
            r = tgt_sprite["rows"]
            c = tgt_sprite["cols"]
            self.tree.item(selected_item, values=(file_path, r, c, new_s))
            dlg.destroy()
            
        btn_save = tk.Button(bottom_frame, text="Сохранить", command=save_scale, bg="#2196F3", fg="white", font=("Arial", 12, "bold"), padx=30, pady=10)
        btn_save.pack(side=tk.RIGHT, padx=50)
        
        # Initial render of target
        render_sprite(cv_tgt, tgt_sprite, scale_val.get(), is_ref=False, frame_idx=dlg.tgt_frame)

        
    def delete_sprite(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Внимание", "Выберите элемент для удаления")
            return
            
        for item in selected_items:
            index = self.tree.index(item)
            self.sprites.pop(index)
            self.tree.delete(item)
            
        self.update_canvas_size_label()

    def get_max_useful_bounds(self, sprite_info, scale=1.0):
        try:
            img = Image.open(sprite_info["path"]).convert("RGBA")
        except Exception:
            return 0, 0
            
        r = sprite_info["rows"]
        c = sprite_info["cols"]
        total = r * c
        frame_w = img.width // c
        frame_h = img.height // r
        
        max_w = 0
        max_h = 0
        for i in range(total):
            s_col = i % c
            s_row = i // c
            frame_img = img.crop((s_col * frame_w, s_row * frame_h, (s_col + 1) * frame_w, (s_row + 1) * frame_h))
            alpha = frame_img.split()[-1]
            bbox = alpha.getbbox()
            if bbox:
                w = bbox[2] - bbox[0]
                h = bbox[3] - bbox[1]
                if w > max_w:
                    max_w = w
                if h > max_h:
                    max_h = h
                    
        return max_w * scale, max_h * scale

    def calc_output_params(self):
        if not self.sprites:
            messagebox.showwarning("Внимание", "Список спрайтов пуст!")
            return
            
        global_max_w = 0
        global_max_h = 0
        max_cols = 0
        
        for sprite_info in self.sprites:
            total_frames = sprite_info["rows"] * sprite_info["cols"]
            max_cols = max(max_cols, total_frames)
            w, h = self.get_max_useful_bounds(sprite_info, scale=sprite_info["scale"])
            global_max_w = max(global_max_w, w)
            global_max_h = max(global_max_h, h)
            
        if global_max_w > 0 and global_max_h > 0:
            new_w = int(global_max_w + 40)
            new_h = int(global_max_h + 40)
            self.out_width_var.set(new_w)
            self.out_height_var.set(new_h)
            self.out_cols_var.set(max_cols)
            messagebox.showinfo("Готово", f"Параметры успешно вычислены:\nШирина кадра: {new_w} px\nВысота кадра: {new_h} px\nМакс. столбцов: {max_cols}")
        else:
            messagebox.showerror("Ошибка", "Не удалось вычислить размеры. Возможно, спрайты пустые.")

    def sync_scales(self):
        if len(self.sprites) < 2:
            messagebox.showwarning("Внимание", "Для синхронизации нужно добавить как минимум 2 спрайтшита!")
            return
            
        # 1. Get reference max height from the first row
        ref_sprite = self.sprites[0]
        _, ref_h = self.get_max_useful_bounds(ref_sprite, scale=ref_sprite["scale"])
        
        if ref_h <= 0:
            messagebox.showerror("Ошибка", "Первый спрайтшит пустой или некорректный. Невозможно вычислить эталонную высоту.")
            return
            
        # 2. Update scales for the rest
        updated_count = 0
        for i in range(1, len(self.sprites)):
            sprite_info = self.sprites[i]
            _, curr_h = self.get_max_useful_bounds(sprite_info, scale=1.0) # unscaled
            
            if curr_h > 0:
                new_scale = round(ref_h / curr_h, 3)
                self.sprites[i]["scale"] = new_scale
                
                # Update treeview
                item_id = self.tree.get_children()[i]
                self.tree.item(item_id, values=(sprite_info["path"], sprite_info["rows"], sprite_info["cols"], new_scale))
                updated_count += 1
                
        messagebox.showinfo("Успех", f"Масштабы успешно синхронизированы для {updated_count} спрайтшитов!")

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
                        
                        # Get bbox to align the useful image
                        alpha = frame_img.split()[-1]
                        bbox = alpha.getbbox()
                        
                        if bbox:
                            # Горизонтально: центрируем именно полезное изображение (bbox)
                            bbox_w = bbox[2] - bbox[0]
                            pos_x = col_idx * out_w + (out_w - bbox_w) // 2 - bbox[0]
                            
                            # Вертикально: выравниваем полезное изображение по низу кадра с отступом 20 px
                            pos_y = row_idx * out_h + out_h - 20 - bbox[3]
                        else:
                            # Если кадр пустой (полностью прозрачный)
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
