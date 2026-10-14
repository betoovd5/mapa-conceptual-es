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
# APLICACIÓN DEL MAPA SINÓPTICO
# ==============================================================================
class SinopticoMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mapa Sinóptico: Auditoría de Base de Datos")
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

        tk.Label(header, text="📋 Mapa Sinóptico: Estructura de Auditoría de BD", font=("Segoe UI", 16, "bold"),
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
                                 text="Haz clic en cualquier concepto de la estructura sinóptica para explorar su descripción y requerimientos de auditoría.",
                                 font=("Segoe UI", 9), fg=COLOR_TEXT_DARK, bg="#ffffff", anchor="w", wraplength=250,
                                 justify="left")
        self.lbl_desc.pack(fill="x", pady=(0, 15))

        self.lbl_det_title = tk.Label(inner, text="Implicación de Seguridad:", font=("Segoe UI", 9, "bold"),
                                      fg=COLOR_TEXT_MUTED, bg="#ffffff")
        self.lbl_det_title.pack(anchor="w", pady=(10, 2))

        self.lbl_details = tk.Label(inner, text="N/A", font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg="#ffffff",
                                    anchor="w", wraplength=250, justify="left")
        self.lbl_details.pack(fill="x")

    def build_nodes(self):
        # Coordenadas ajustadas para centrarse de izquierda a derecha
        self.nodes = [
            InteractiveNode("root_s", 100, 260, 160, 45, "Auditoría de BD", "Raíz",
                            "El proceso de auditoría de bases de datos se divide en tres enfoques cronológicos esenciales: Preventiva, Detectiva y Correctiva, asegurando la integridad global.",
                            "Involucra el rastreo de eventos, mitigación activa y mantenimiento de controles robustos antes, durante y después de cualquier incidente.",
                            "root"),

            # NIVEL 2 - PREVENTIVA
            InteractiveNode("prev", 340, 100, 150, 36, "Auditoría Preventiva", "Tipo de Auditoría",
                            "Enfoque enfocado a reducir la superficie de ataque y configurar defensas robustas antes de que ocurran brechas de seguridad.",
                            "Establece líneas base seguras y políticas administrativas de control de accesos.",
                            "process"),
            InteractiveNode("ctrl_acc", 600, 50, 220, 32, "Control de Accesos", "Preventivo",
                            "Políticas estrictas para asegurar que solo los usuarios verificados interactúen con datos sensibles.",
                            "Implementa autenticación multifactor, rotación obligatoria de contraseñas y control por IP.",
                            "concept"),
            InteractiveNode("hard", 600, 100, 220, 32, "Hardening de BD", "Preventivo",
                            "Ajuste y blindaje de la configuración del servidor de base de datos eliminando servicios y puertos innecesarios.",
                            "Mantiene al día los parches de seguridad recomendados por el proveedor del motor de BD.",
                            "concept"),
            InteractiveNode("roles", 600, 150, 220, 32, "Roles y Privilegios", "Preventivo",
                            "Asignación lógica y rigurosa de los accesos según el rol de cada usuario o aplicación.",
                            "Sigue el principio de mínimo privilegio técnico para evitar la escalación maliciosa de permisos.",
                            "concept"),

            # NIVEL 2 - DETECTIVA
            InteractiveNode("det", 340, 260, 150, 36, "Auditoría Detectiva", "Tipo de Auditoría",
                            "Procedimientos reactivos encargados de identificar accesos sospechosos o ataques en tiempo real.",
                            "Monitorea el tráfico de red de consultas y analiza comportamientos atípicos.", "process"),
            InteractiveNode("logs", 600, 210, 220, 32, "Registro de Actividad", "Detectivo",
                            "Auditoría sistemática que registra comandos DML (SELECT, UPDATE) y DDL (ALTER, DROP) ejecutados.",
                            "Guarda metadatos críticos: usuario ejecutor, dirección IP de origen y marca de tiempo exacta.",
                            "concept"),
            InteractiveNode("alertas", 600, 260, 220, 32, "Alertas de Intentos Fallidos", "Detectivo",
                            "Alarmas automáticas disparadas ante comportamientos sospechosos o repetitivos.",
                            "Notifica inmediatamente al equipo de SecOps si se detecta un pico de credenciales incorrectas (brute-force).",
                            "concept"),
            InteractiveNode("triggers", 600, 310, 220, 32, "Triggers de Auditoría", "Detectivo",
                            "Disparadores incrustados en BD para auditar modificaciones en el contenido de las tablas críticas.",
                            "Guardan un historial de cambios 'antes' y 'después' para asegurar la trazabilidad del dato.",
                            "concept"),

            # NIVEL 2 - CORRECTIVA
            InteractiveNode("corr", 340, 420, 150, 36, "Auditoría Correctiva", "Tipo de Auditoría",
                            "Acciones correctivas diseñadas para responder y mitigar daños después de detectarse un incidente de seguridad.",
                            "Busca recuperar la consistencia de la base de datos y aislar la amenaza identificada.",
                            "process"),
            InteractiveNode("forense", 600, 370, 220, 32, "Análisis Forense", "Correctivo",
                            "Investigación exhaustiva post-ataque para determinar la causa raíz del fallo de seguridad.",
                            "Determina qué tablas se comprometieron y qué brecha de seguridad fue explotada por el atacante.",
                            "concept"),
            InteractiveNode("backups", 600, 420, 220, 32, "Restauración Segura", "Correctivo",
                            "Plan de continuidad para levantar el servicio a partir de respaldos periódicos certificados como libres de malware.",
                            "Requiere validaciones programadas de la integridad del backup de forma regular.",
                            "concept"),
            InteractiveNode("mitig", 600, 470, 220, 32, "Acciones de Mitigación", "Correctivo",
                            "Bloqueo inmediato de accesos, revocación de roles comprometidos y aislamiento de redes afectadas.",
                            "Detiene la propagación del ataque de manera coordinada mientras se implementa una solución definitiva.",
                            "concept")
        ]

    def draw_curly_brace(self, canvas, draw, x, y1, y2, w=15, r=10, color="#2563eb", thickness=2):
        yc = (y1 + y2) / 2
        if y2 - y1 < 4 * r:
            r = (y2 - y1) / 4

        def bezier_pts(p0, p1, p2, p3):
            return [
                ((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0],
                 (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1])
                for t in [i / 10.0 for i in range(11)]
            ]

        pts = []
        # 1. Gancho superior bezier
        pts.extend(bezier_pts((x + w, y1), (x + w / 2, y1), (x, y1 + r / 2), (x, y1 + r)))
        # 2. Línea recta
        pts.append((x, yc - r))
        # 3. Curva media superior (punta izquierda)
        pts.extend(bezier_pts((x, yc - r), (x, yc - r / 2), (x - w, yc - r / 2), (x - w, yc)))
        # 4. Curva media inferior
        pts.extend(bezier_pts((x - w, yc), (x - w, yc + r / 2), (x, yc + r / 2), (x, yc + r)))
        # 5. Línea recta
        pts.append((x, y2 - r))
        # 6. Gancho inferior bezier
        pts.extend(bezier_pts((x, y2 - r), (x, y2 - r / 2), (x + w / 2, y2), (x + w, y2)))

        flat_pts = [coord for pt in pts for coord in pt]
        canvas.create_line(flat_pts, fill=color, width=thickness, smooth=True)

        if draw:
            # CORRECCIÓN CLAVE: Convertir coordenadas y espesor a ENTEROS para PIL
            int_pts = [(int(px), int(py)) for px, py in pts]
            draw.line(int_pts, fill=color, width=int(thickness))

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
        # Llave principal entre Raíz y los tres tipos de auditoría (y: 100 a 420)
        self.draw_curly_brace(self.canvas, self.pil_draw, 215, 100, 420, w=20, r=10, color=COLOR_ACCENT, thickness=2.5)

        self.canvas.create_line(180, 260, 195, 260, fill=COLOR_TEXT_MUTED, width=1.5)
        self.pil_draw.line([(180, 260), (195, 260)], fill="#94a3b8", width=2)

        for y in [100, 260, 420]:
            self.canvas.create_line(215, y, 265, y, fill=COLOR_TEXT_MUTED, width=1.5)
            self.pil_draw.line([(215, y), (265, y)], fill="#94a3b8", width=2)

        # Llaves secundarias
        # 1. Preventiva (y: 50 a 150)
        self.draw_curly_brace(self.canvas, self.pil_draw, 440, 50, 150, w=12, r=8, color="#10b981", thickness=1.8)
        self.canvas.create_line(415, 100, 428, 100, fill=COLOR_TEXT_MUTED, width=1.5)
        self.pil_draw.line([(415, 100), (428, 100)], fill="#94a3b8", width=2)
        for y in [50, 100, 150]:
            self.canvas.create_line(440, y, 490, y, fill=COLOR_TEXT_MUTED, width=1.5)
            self.pil_draw.line([(440, y), (490, y)], fill="#94a3b8", width=2)

        # 2. Detectiva (y: 210 a 310)
        self.draw_curly_brace(self.canvas, self.pil_draw, 440, 210, 310, w=12, r=8, color="#f59e0b", thickness=1.8)
        self.canvas.create_line(415, 260, 428, 260, fill=COLOR_TEXT_MUTED, width=1.5)
        self.pil_draw.line([(415, 260), (428, 260)], fill="#94a3b8", width=2)
        for y in [210, 260, 310]:
            self.canvas.create_line(440, y, 490, y, fill=COLOR_TEXT_MUTED, width=1.5)
            self.pil_draw.line([(440, y), (490, y)], fill="#94a3b8", width=2)

        # 3. Correctiva (y: 370 a 470)
        self.draw_curly_brace(self.canvas, self.pil_draw, 440, 370, 470, w=12, r=8, color="#ef4444", thickness=1.8)
        self.canvas.create_line(415, 420, 428, 420, fill=COLOR_TEXT_MUTED, width=1.5)
        self.pil_draw.line([(415, 420), (428, 420)], fill="#94a3b8", width=2)
        for y in [370, 420, 470]:
            self.canvas.create_line(440, y, 490, y, fill=COLOR_TEXT_MUTED, width=1.5)
            self.pil_draw.line([(440, y), (490, y)], fill="#94a3b8", width=2)

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
        return COLOR_NODE_CONCEPT_BORDER

    def update_details(self, node):
        if node is None:
            self.lbl_title.configure(text="Selecciona un concepto", fg=COLOR_TEXT_DARK)
            self.lbl_badge.configure(text="CONCEPTO GENERAL", bg=COLOR_TEXT_MUTED)
            self.lbl_desc.configure(
                text="Haz clic en cualquier concepto de la estructura sinóptica para explorar su descripción y requerimientos de auditoría.")
            self.lbl_details.configure(text="N/A")
            return

        self.lbl_title.configure(text=node.name, fg=COLOR_ACCENT)
        self.lbl_badge.configure(text=node.category.upper())
        if node.node_type == "root":
            self.lbl_badge.configure(bg="#6b21a8")
        elif node.node_type == "process":
            self.lbl_badge.configure(bg="#166534")
        else:
            self.lbl_badge.configure(bg=COLOR_ACCENT)

        self.lbl_desc.configure(text=node.description)
        self.lbl_details.configure(text=node.details)

    def export_map(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imagen PNG", "*.png")],
            initialfile="mapa_sinoptico.png",
            title="Guardar Mapa Sinóptico"
        )
        if filepath:
            try:
                self.pil_img.save(filepath, "PNG")
                messagebox.showinfo("Exportación Exitosa", f"Guardado correctamente en:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SinopticoMapApp(root)
    root.mainloop()
