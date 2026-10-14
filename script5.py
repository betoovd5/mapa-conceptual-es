import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
from PIL import Image, ImageDraw, ImageFont

# ==============================================================================
# CONFIGURACIÓN DE COLORES
# ==============================================================================
COLOR_APP_BG = "#f8fafc"
COLOR_CANVAS_BG = "#ffffff"
COLOR_GRID = "#f1f5f9"
COLOR_TEXT_DARK = "#0f172a"
COLOR_TEXT_MUTED = "#64748b"
COLOR_ACCENT = "#2563eb"
COLOR_ACCENT_HOVER = "#1d4ed8"

COLOR_NODE_ROOT = "#faf5ff"
COLOR_NODE_ROOT_BORDER = "#e9d5ff"
COLOR_NODE_PROCESS = "#f0fdf4"
COLOR_NODE_PROCESS_BORDER = "#bbf7d0"
COLOR_NODE_CONCEPT = "#eff6ff"
COLOR_NODE_CONCEPT_BORDER = "#bfdbfe"
COLOR_NODE_METRIC = "#fffbeb"
COLOR_NODE_METRIC_BORDER = "#fde68a"
COLOR_HIGHLIGHT = "#f59e0b"


# ==============================================================================
# CLASE DE NODO INTERACTIVO
# ==============================================================================
class InteractiveNode:
    def __init__(self, key, x, y, w, h, name, category, description, details, node_type="concept"):
        self.key = key
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = name
        self.category = category
        self.description = description
        self.details = details
        self.node_type = node_type
        self.canvas_ids = []

    def contains(self, px, py):
        x1 = self.x - self.w / 2
        x2 = self.x + self.w / 2
        y1 = self.y - self.h / 2
        y2 = self.y + self.h / 2
        return x1 <= px <= x2 and y1 <= py <= y2

    def get_bounds(self):
        return (self.x - self.w / 2, self.y - self.h / 2, self.x + self.w / 2, self.y + self.h / 2)


# ==============================================================================
# APLICACIÓN DEL MAPA DE SOL
# ==============================================================================
class SolMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mapa de Sol: Monitoreo Continuo de BD")
        self.root.geometry("1080x680")
        self.root.minsize(900, 500)
        self.root.configure(bg=COLOR_APP_BG)

        try:
            self.pil_font_title = ImageFont.truetype("arial.ttf", 15)
            self.pil_font_body = ImageFont.truetype("arial.ttf", 10)
            self.pil_font_bold = ImageFont.truetype("arialbd.ttf", 11)
        except IOError:
            self.pil_font_title = ImageFont.load_default()
            self.pil_font_body = ImageFont.load_default()
            self.pil_font_bold = ImageFont.load_default()

        self.nodes = []
        self.hovered_node = None
        self.selected_node = None

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_rowconfigure(0, weight=1)

        self.setup_ui()
        self.build_nodes()
        self.redraw()

    def setup_ui(self):
        # Área del Canvas (Izquierda)
        canvas_frame = tk.Frame(self.root, bg=COLOR_APP_BG)
        canvas_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        header = tk.Frame(canvas_frame, bg=COLOR_APP_BG)
        header.pack(fill="x", pady=(0, 10))

        tk.Label(header, text="☀️ Mapa de Sol: Monitoreo Continuo de BD", font=("Segoe UI", 16, "bold"),
                 fg=COLOR_TEXT_DARK, bg=COLOR_APP_BG).pack(side="left")

        btn_export = tk.Button(header, text="💾 Guardar Imagen PNG", font=("Segoe UI", 9, "bold"), fg="#ffffff",
                               bg=COLOR_ACCENT,
                               activebackground=COLOR_ACCENT_HOVER, activeforeground="#ffffff", relief="flat", bd=0,
                               cursor="hand2", command=self.export_map, padx=12, pady=6)
        btn_export.pack(side="right")

        self.canvas = tk.Canvas(canvas_frame, bg=COLOR_CANVAS_BG, highlightthickness=1, highlightbackground=COLOR_GRID)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Motion>", self.on_canvas_hover)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Panel de Detalles (Derecha)
        self.panel_details = tk.Frame(self.root, bg="#ffffff", width=280, highlightthickness=1,
                                      highlightbackground=COLOR_GRID)
        self.panel_details.grid(row=0, column=1, sticky="nsew")
        self.panel_details.grid_propagate(False)

        inner = tk.Frame(self.panel_details, bg="#ffffff", padx=15, pady=20)
        inner.pack(fill="both", expand=True)

        tk.Label(inner, text="DETALLES DEL NODO", font=("Segoe UI", 9, "bold"), fg=COLOR_TEXT_MUTED, bg="#ffffff").pack(
            anchor="w", pady=(0, 15))

        self.lbl_title = tk.Label(inner, text="Selecciona un concepto", font=("Segoe UI", 13, "bold"),
                                  fg=COLOR_TEXT_DARK, bg="#ffffff", anchor="w", wraplength=250, justify="left")
        self.lbl_title.pack(fill="x", pady=(0, 5))

        self.lbl_badge = tk.Label(inner, text="Concepto General", font=("Segoe UI", 8, "bold"), fg="#ffffff",
                                  bg=COLOR_TEXT_MUTED, padx=6, pady=1)
        self.lbl_badge.pack(anchor="w", pady=(0, 15))

        self.lbl_desc = tk.Label(inner,
                                 text="Haz clic en cualquier nodo o rayo del mapa de sol para explorar sus dimensiones métricas y de auditoría.",
                                 font=("Segoe UI", 9), fg=COLOR_TEXT_DARK, bg="#ffffff", anchor="w", wraplength=250,
                                 justify="left")
        self.lbl_desc.pack(fill="x", pady=(0, 15))

        self.lbl_det_title = tk.Label(inner, text="Implicación de Monitoreo:", font=("Segoe UI", 9, "bold"),
                                      fg=COLOR_TEXT_MUTED, bg="#ffffff")
        self.lbl_det_title.pack(anchor="w", pady=(10, 2))

        self.lbl_details = tk.Label(inner, text="N/A", font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg="#ffffff",
                                    anchor="w", wraplength=250, justify="left")
        self.lbl_details.pack(fill="x")

    def build_nodes(self):
        cx, cy = 370, 280

        # Nodo central (El Sol)
        self.nodes = [
            InteractiveNode("root_sol", cx, cy, 140, 45, "Monitoreo de BD", "Raíz",
                            "El monitoreo continuo de bases de datos representa un proceso de control de 360 grados en tiempo real para supervisar la salud del motor.",
                            "Cubre cuatro dimensiones operativas cruciales: Rendimiento, Seguridad, Almacenamiento y Disponibilidad del sistema.",
                            "root")
        ]

        self.categories = [
            {
                "key": "rend", "name": "Rendimiento", "angle": 315, "color": "#f97316",
                "desc": "Análisis del uso de hardware y velocidad de respuesta de las transacciones.",
                "details": "Garantiza que el usuario final no experimente lentitud por consultas ineficientes.",
                "metrics": [
                    ("cpu", "CPU y Memoria", "Uso de RAM y CPU por el proceso del motor de BD."),
                    ("lentas", "Queries Lentas",
                     "Registro y alertas de sentencias SQL que exceden el tiempo máximo de respuesta."),
                    ("pool", "Pool de Conexiones", "Supervisión de conexiones simultáneas y sockets activos.")
                ]
            },
            {
                "key": "seg", "name": "Seguridad", "angle": 45, "color": "#ef4444",
                "desc": "Monitoreo de integridad, intentos de accesos y cumplimiento de directivas.",
                "details": "Ayuda a repeler amenazas informáticas y abusos de privilegios administrativos.",
                "metrics": [
                    ("fallidos", "Acceso Fallido",
                     "Picos de autenticación errónea compatibles con ataques de fuerza bruta."),
                    ("inyec", "Inyecciones SQL",
                     "Detección heurística de código SQL malicioso inyectado desde la aplicación."),
                    ("roles_alt", "Roles Alterados",
                     "Rastreo de comandos DDL (GRANT, ALTER) de escalación de privilegios.")
                ]
            },
            {
                "key": "alm", "name": "Almacenamiento", "angle": 135, "color": "#3b82f6",
                "desc": "Control de espacio físico libre de los datafiles y los logs de transacciones.",
                "details": "Previene caídas del motor de BD por fallas de escritura física en disco.",
                "metrics": [
                    ("disco", "Espacio en Disco", "Porcentaje de espacio libre en los discos del servidor de datos."),
                    ("crec_tab", "Crecimiento Tablas",
                     "Supervisión histórica para particionar tablas grandes o archivar datos antiguos."),
                    ("tempdb", "Uso de TempDB",
                     "Métricas del uso de base de datos temporal para ordenamientos complejos.")
                ]
            },
            {
                "key": "disp", "name": "Disponibilidad", "angle": 225, "color": "#10b981",
                "desc": "Monitoreo del Uptime del servicio y copias de seguridad activas.",
                "details": "Garantiza el cumplimiento de los acuerdos de nivel de servicio (SLA).",
                "metrics": [
                    ("uptime", "Uptime Servicio",
                     "Porcentaje mensual de operatividad de la instancia de base de datos."),
                    ("repl_status", "Replicación BD",
                     "Estado de salud de los nodos secundarios en arquitecturas AlwaysOn o réplicas."),
                    ("back_ok", "Estatus Backups",
                     "Validación diaria de la ejecución e integridad de los backups del sistema.")
                ]
            }
        ]

        d_cat = 150
        d_metric = 100

        for cat in self.categories:
            rad = math.radians(cat["angle"])
            cx_cat = cx + d_cat * math.cos(rad)
            cy_cat = cy + d_cat * math.sin(rad)

            node_cat = InteractiveNode(cat["key"], cx_cat, cy_cat, 110, 32, cat["name"], "Dimensión", cat["desc"],
                                       cat["details"], "process")
            self.nodes.append(node_cat)

            for i, (m_key, m_name, m_desc) in enumerate(cat["metrics"]):
                sub_angle = cat["angle"] + (i - 1) * 30
                sub_rad = math.radians(sub_angle)

                cx_metric = cx_cat + d_metric * math.cos(sub_rad)
                cy_metric = cy_cat + d_metric * math.sin(sub_rad)

                node_metric = InteractiveNode(m_key, cx_metric, cy_metric, 95, 30, m_name, cat["name"], m_desc,
                                              "Métrica de monitoreo continuo para supervisar la salud de la base de datos.",
                                              "metric")
                self.nodes.append(node_metric)

    def redraw(self):
        self.canvas.delete("all")
        self.canvas.update()
        cw = max(self.canvas.winfo_width(), 750)
        ch = max(self.canvas.winfo_height(), 580)

        self.pil_img = Image.new("RGB", (cw, ch), "#ffffff")
        self.pil_draw = ImageDraw.Draw(self.pil_img)

        self.draw_grid(cw, ch)
        self.draw_connections()

        for node in self.nodes:
            self.draw_node(node)

    def draw_grid(self, cw, ch):
        for x in range(0, cw, 40):
            self.canvas.create_line(x, 0, x, ch, fill=COLOR_GRID, dash=(2, 4))
            self.pil_draw.line([(x, 0), (x, ch)], fill="#fafafa")
        for y in range(0, ch, 40):
            self.canvas.create_line(0, y, cw, y, fill=COLOR_GRID, dash=(2, 4))
            self.pil_draw.line([(0, y), (cw, y)], fill="#fafafa")

    def draw_node(self, node):
        x1, y1, x2, y2 = node.get_bounds()
        node.canvas_ids = []

        bg_color = COLOR_NODE_CONCEPT
        border_color = COLOR_NODE_CONCEPT_BORDER
        text_color = COLOR_TEXT_DARK

        if node.node_type == "root":
            bg_color = COLOR_NODE_ROOT
            border_color = COLOR_NODE_ROOT_BORDER
        elif node.node_type == "process":
            bg_color = COLOR_NODE_PROCESS
            border_color = COLOR_NODE_PROCESS_BORDER
        elif node.node_type == "metric":
            bg_color = COLOR_NODE_METRIC
            border_color = COLOR_NODE_METRIC_BORDER

        border_width = 1
        if node == self.selected_node:
            border_color = COLOR_HIGHLIGHT
            border_width = 3
        elif node == self.hovered_node:
            border_color = COLOR_HIGHLIGHT
            border_width = 2

        rect_ids = self.canvas_rounded_rect(self.canvas, x1, y1, x2, y2, r=6, fill=bg_color, outline=border_color,
                                            width=border_width)
        node.canvas_ids.extend(rect_ids)
        node.rect_id = rect_ids[0] if rect_ids else None

        self.pil_draw.rounded_rectangle([int(x1), int(y1), int(x2), int(y2)], radius=6, fill=bg_color,
                                        outline=border_color, width=int(border_width))

        font_tk = ("Segoe UI", 9, "bold" if node.node_type == "root" else "normal")
        font_pil = self.pil_font_bold if node.node_type == "root" else self.pil_font_body

        text_id = self.canvas.create_text(node.x, node.y, text=node.name, font=font_tk, fill=text_color,
                                          justify="center", width=node.w - 12)
        node.canvas_ids.append(text_id)

        lines = self.wrap_text(node.name, font_pil, node.w - 12)
        line_height = 13
        total_h = len(lines) * line_height
        start_y = node.y - total_h / 2

        for i, line in enumerate(lines):
            line_w = self.pil_draw.textlength(line, font=font_pil)
            lx = node.x - line_w / 2
            ly = start_y + i * line_height
            self.pil_draw.text((int(lx), int(ly)), line, font=font_pil, fill=text_color)

    def canvas_rounded_rect(self, canvas, x1, y1, x2, y2, r=8, fill="", outline="", width=1):
        id_list = []
        if fill:
            id_list.append(
                canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, style="pieslice", fill=fill,
                                  outline=""))
            id_list.append(
                canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, style="pieslice", fill=fill,
                                  outline=""))
            id_list.append(
                canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, style="pieslice", fill=fill,
                                  outline=""))
            id_list.append(
                canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, style="pieslice", fill=fill,
                                  outline=""))
            id_list.append(canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=fill, outline=""))
            id_list.append(canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=fill, outline=""))
        if outline:
            id_list.append(
                canvas.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, style="arc", outline=outline,
                                  width=width))
            id_list.append(
                canvas.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, style="arc", outline=outline,
                                  width=width))
            id_list.append(
                canvas.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, style="arc", outline=outline,
                                  width=width))
            id_list.append(
                canvas.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, style="arc", outline=outline,
                                  width=width))
            id_list.append(canvas.create_line(x1 + r, y1, x2 - r, y1, fill=outline, width=width))
            id_list.append(canvas.create_line(x1 + r, y2, x2 - r, y2, fill=outline, width=width))
            id_list.append(canvas.create_line(x1, y1 + r, x1, y2 - r, fill=outline, width=width))
            id_list.append(canvas.create_line(x2, y1 + r, x2, y2 - r, fill=outline, width=width))
        return id_list

    def wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        current = []
        for w in words:
            test = " ".join(current + [w])
            if self.pil_draw.textlength(test, font=font) <= max_width:
                current.append(w)
            else:
                lines.append(" ".join(current))
                current = [w]
        if current:
            lines.append(" ".join(current))
        return lines

    def draw_connections(self):
        cx, cy = 370, 280

        for cat in self.categories:
            rad = math.radians(cat["angle"])
            cx_cat = cx + 150 * math.cos(rad)
            cy_cat = cy + 150 * math.sin(rad)

            # Línea al centro (Rayo principal del sol)
            self.canvas.create_line(cx + 40 * math.cos(rad), cy + 20 * math.sin(rad),
                                    cx_cat - 55 * math.cos(rad), cy_cat - 16 * math.sin(rad),
                                    fill=cat["color"], width=3)

            # CORRECCIÓN PIL: Convertir floats a enteros para dibujar líneas
            self.pil_draw.line([(int(cx + 40 * math.cos(rad)), int(cy + 20 * math.sin(rad))),
                                (int(cx_cat - 55 * math.cos(rad)), int(cy_cat - 16 * math.sin(rad)))],
                               fill=cat["color"], width=3)

            for i, (m_key, m_name, m_desc) in enumerate(cat["metrics"]):
                sub_angle = cat["angle"] + (i - 1) * 30
                sub_rad = math.radians(sub_angle)

                cx_metric = cx_cat + 100 * math.cos(sub_rad)
                cy_metric = cy_cat + 100 * math.sin(sub_rad)

                self.canvas.create_line(cx_cat + 25 * math.cos(sub_rad), cy_cat + 12 * math.sin(sub_rad),
                                        cx_metric - 35 * math.cos(sub_rad), cy_metric - 10 * math.sin(sub_rad),
                                        fill=COLOR_TEXT_MUTED, width=1.5)

                # CORRECCIÓN PIL: Convertir floats a enteros
                self.pil_draw.line([(int(cx_cat + 25 * math.cos(sub_rad)), int(cy_cat + 12 * math.sin(sub_rad))),
                                    (int(cx_metric - 35 * math.cos(sub_rad)), int(cy_metric - 10 * math.sin(sub_rad)))],
                                   fill="#94a3b8", width=1)

    def on_canvas_hover(self, event):
        node = self.get_node_at(event.x, event.y)
        if node != self.hovered_node:
            if self.hovered_node and self.hovered_node != self.selected_node:
                self.set_node_border(self.hovered_node, self.get_default_border(self.hovered_node), 1)
            self.hovered_node = node
            if node and node != self.selected_node:
                self.set_node_border(node, COLOR_HIGHLIGHT, 2)
                self.canvas.configure(cursor="hand2")
            elif not node:
                self.canvas.configure(cursor="")

    def on_canvas_click(self, event):
        node = self.get_node_at(event.x, event.y)
        if self.selected_node:
            self.set_node_border(self.selected_node, self.get_default_border(self.selected_node), 1)
        if node:
            self.selected_node = node
            self.set_node_border(node, COLOR_HIGHLIGHT, 3)
            self.update_details(node)
        else:
            self.selected_node = None
            self.update_details(None)

    def get_node_at(self, px, py):
        for node in reversed(self.nodes):
            if node.contains(px, py):
                return node
        return None

    def set_node_border(self, node, color, width=1):
        for cid in node.canvas_ids:
            ftype = self.canvas.type(cid)
            if ftype in ["arc", "line", "rectangle"]:
                if ftype == "line":
                    self.canvas.itemconfig(cid, fill=color, width=width)
                elif ftype == "arc":
                    style = self.canvas.itemcget(cid, "style")
                    if style == "arc":
                        self.canvas.itemconfig(cid, outline=color, width=width)
                elif ftype == "rectangle":
                    outline = self.canvas.itemcget(cid, "outline")
                    if outline:
                        self.canvas.itemconfig(cid, outline=color, width=width)

    def get_default_border(self, node):
        if node.node_type == "root": return COLOR_NODE_ROOT_BORDER
        if node.node_type == "process": return COLOR_NODE_PROCESS_BORDER
        return COLOR_NODE_METRIC_BORDER

    def update_details(self, node):
        if node is None:
            self.lbl_title.configure(text="Selecciona un concepto", fg=COLOR_TEXT_DARK)
            self.lbl_badge.configure(text="CONCEPTO GENERAL", bg=COLOR_TEXT_MUTED)
            self.lbl_desc.configure(
                text="Haz clic en cualquier nodo o rayo del mapa de sol para explorar sus dimensiones métricas y de auditoría.")
            self.lbl_details.configure(text="N/A")
            return

        self.lbl_title.configure(text=node.name, fg=COLOR_ACCENT)
        self.lbl_badge.configure(text=node.category.upper())
        if node.node_type == "root":
            self.lbl_badge.configure(bg="#6b21a8")
        elif node.node_type == "process":
            self.lbl_badge.configure(bg="#166534")
        else:
            self.lbl_badge.configure(bg=COLOR_HIGHLIGHT)

        self.lbl_desc.configure(text=node.description)
        self.lbl_details.configure(text=node.details)

    def export_map(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imagen PNG", "*.png")],
            initialfile="mapa_sol.png",
            title="Guardar Mapa de Sol"
        )
        if filepath:
            try:
                self.pil_img.save(filepath, "PNG")
                messagebox.showinfo("Exportación Exitosa", f"Guardado correctamente en:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SolMapApp(root)
    root.mainloop()