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
# APLICACIÓN DEL MAPA CONCEPTUAL
# ==============================================================================
class ConceptualMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mapa Conceptual: Migración de la B. D. (Seguridad)")
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

        tk.Label(header, text="📌 Mapa Conceptual: Migración Segura de BD", font=("Segoe UI", 16, "bold"),
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
                                 text="Haz clic en cualquier nodo para ver su descripción, requerimientos de seguridad e implicación técnica.",
                                 font=("Segoe UI", 9), fg=COLOR_TEXT_DARK, bg="#ffffff", anchor="w", wraplength=250,
                                 justify="left")
        self.lbl_desc.pack(fill="x", pady=(0, 15))

        self.lbl_det_title = tk.Label(inner, text="Implicación Técnica:", font=("Segoe UI", 9, "bold"),
                                      fg=COLOR_TEXT_MUTED, bg="#ffffff")
        self.lbl_det_title.pack(anchor="w", pady=(10, 2))

        self.lbl_details = tk.Label(inner, text="N/A", font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg="#ffffff",
                                    anchor="w", wraplength=250, justify="left")
        self.lbl_details.pack(fill="x")

    def build_nodes(self):
        # Coordenadas ajustadas para centrarse en un lienzo de aproximadamente 750x580
        self.nodes = [
            InteractiveNode("root", 360, 50, 200, 45, "Migración de la B.D. (Seguridad)", "Raíz",
                            "El proceso de migración de base de datos bajo estrictos lineamientos de seguridad para asegurar la protección contra accesos no autorizados y fugas.",
                            "Requiere una metodología de tres fases: Planificación rigurosa, Transferencia segura cifrada e Integridad Post-Migración con validación completa.",
                            "root"),

            # FASE 1
            InteractiveNode("fase1", 140, 170, 110, 36, "1. Planificación", "Proceso",
                            "Primera etapa donde se diseña la estrategia de migración, minimizando riesgos y evaluando dependencias del sistema.",
                            "Involucra un plan de rollback, análisis de ventanas de mantenimiento, y el inventario formal de los datos sensibles.",
                            "process"),
            InteractiveNode("riesgos", 70, 270, 110, 36, "Evaluación de Riesgos", "Subfase",
                            "Identificación previa de posibles fallas, cuellos de botella e interrupciones del servicio durante el proceso de copia.",
                            "Su objetivo primordial es mitigar o eliminar por completo el riesgo de fuga o secuestro de datos (Ransomware).",
                            "concept"),
            InteractiveNode("fugas", 70, 370, 110, 36, "Fugas de Información", "Objetivo",
                            "Salida de información confidencial o restringida fuera de la frontera de seguridad de la organización.",
                            "Se previene controlando estrictamente las conexiones de red y utilizando solo canales autenticados en producción.",
                            "concept"),
            InteractiveNode("clasif", 210, 270, 110, 36, "Clasificación de Datos", "Subfase",
                            "Identificación y etiquetado de la información según su nivel de confidencialidad para determinar las medidas de cifrado.",
                            "Separa la base de datos en categorías: Pública, Interna, Confidencial o de Seguridad Nacional.",
                            "concept"),
            InteractiveNode("sensibles", 210, 370, 110, 36, "Datos Sensibles", "Objetivo",
                            "Información sujeta a leyes y regulaciones como GDPR o PCI-DSS (números de tarjeta, datos personales).",
                            "Este tipo de datos requiere tratamiento especial como el enmascaramiento dinámico (data masking) en ambientes no productivos.",
                            "concept"),

            # FASE 2
            InteractiveNode("fase2", 360, 170, 110, 36, "2. Transferencia", "Proceso",
                            "Ejecución física del movimiento de datos del servidor origen al destino. Es el punto más vulnerable.",
                            "Debe realizarse mediante túneles seguros y redes privadas virtuales (VPN), asegurando confidencialidad.",
                            "process"),
            InteractiveNode("cifrado", 290, 270, 110, 36, "Cifrado de Datos", "Subfase",
                            "Codificación criptográfica de la información para evitar que personas no autorizadas intercepten y lea los datos.",
                            "Es la defensa de última línea ante vulnerabilidades en la red o acceso directo al almacenamiento físico.",
                            "concept"),
            InteractiveNode("transito", 220, 370, 110, 36, "Tránsito (TLS 1.3)", "Estándar",
                            "Protocolo criptográfico moderno utilizado para encriptar la comunicación activa en el cable de red.",
                            "Evita ataques Man-in-the-Middle (intercepción en vivo). Reemplaza versiones obsoletas como SSL o TLS 1.0.",
                            "concept"),
            InteractiveNode("reposo", 360, 370, 110, 36, "Reposo (AES-256)", "Estándar",
                            "Cifrado del almacenamiento físico: archivos de datos (.mdf, .db), logs de transacciones y archivos de backup.",
                            "Se implementa con TDE (Transparent Data Encryption) o a nivel de sistema operativo para proteger discos robados.",
                            "concept"),
            InteractiveNode("integ", 430, 270, 110, 36, "Integridad de Datos", "Subfase",
                            "Garantía de que los datos copiados son idénticos al origen y no han sufrido alteraciones accidentales o maliciosas.",
                            "Se valida con rutinas automáticas al final del copiado de cada tabla o volumen de datos.",
                            "concept"),
            InteractiveNode("hash", 490, 370, 110, 36, "Hashes (SHA-256)", "Estándar",
                            "Algoritmo criptográfico de un solo sentido que genera un valor único hash para cada archivo o tabla de base de datos.",
                            "Se compara el hash del origen y el destino. Si difieren, indica corrupción y se ejecuta un rollback.",
                            "concept"),

            # FASE 3
            InteractiveNode("fase3", 580, 170, 110, 36, "3. Post-Migración", "Proceso",
                            "Última etapa enfocada en la verificación general de consistencia y restauración segura de los accesos.",
                            "Incluye pruebas de rendimiento de consultas (tuning) y la habilitación de monitores continuos.",
                            "process"),
            InteractiveNode("valid", 510, 270, 110, 36, "Validación de Esquema", "Subfase",
                            "Verificación estructural que compara tablas, índices, llaves primarias/foráneas, triggers y vistas entre origen y destino.",
                            "Previene problemas funcionales en las aplicaciones por la ausencia de restricciones u objetos olvidados.",
                            "concept"),
            InteractiveNode("consist", 510, 370, 110, 36, "Consistencia de BD", "Objetivo",
                            "Garantiza que todas las transacciones se consoliden correctamente de acuerdo con las reglas de integridad referencial.",
                            "Previene el desastre de tener registros huérfanos o datos lógicamente inválidos en la base destino.",
                            "concept"),
            InteractiveNode("acceso", 650, 270, 110, 36, "Control de Accesos", "Subfase",
                            "Reconfiguración de credenciales de usuario y esquemas de permisos en la nueva infraestructura.",
                            "Involucra la rotación obligatoria de contraseñas de las cuentas de servicio del sistema.",
                            "concept"),
            InteractiveNode("priv", 650, 370, 110, 36, "Mínimo Privilegio", "Objetivo",
                            "Principio de seguridad donde cada aplicación y usuario posee únicamente los permisos necesarios para su función.",
                            "Exige la autenticación multifactor (MFA) para todas las conexiones administrativas o privilegios elevados.",
                            "concept"),
        ]

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

        # PIL draw (convert boundaries to integer)
        self.pil_draw.rounded_rectangle([int(x1), int(y1), int(x2), int(y2)], radius=6, fill=bg_color,
                                        outline=border_color, width=int(border_width))

        font_tk = ("Segoe UI", 9, "bold" if node.node_type == "root" else "normal")
        font_pil = self.pil_font_bold if node.node_type == "root" else self.pil_font_body

        text_id = self.canvas.create_text(node.x, node.y, text=node.name, font=font_tk, fill=text_color,
                                          justify="center", width=node.w - 12)
        node.canvas_ids.append(text_id)

        # Text wrap in PIL
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
        connections = [
            ("root", "fase1", "debe planificarse"),
            ("root", "fase2", "ejecuta mediante"),
            ("root", "fase3", "concluye con"),

            ("fase1", "riesgos", "evalúa"),
            ("riesgos", "fugas", "previene"),
            ("fase1", "clasif", "ejecuta"),
            ("clasif", "sensibles", "categoriza"),

            ("fase2", "cifrado", "requiere"),
            ("cifrado", "transito", "en"),
            ("cifrado", "reposo", "en"),
            ("fase2", "integ", "asegura"),
            ("integ", "hash", "mediante"),

            ("fase3", "valid", "realiza"),
            ("valid", "consist", "garantiza"),
            ("fase3", "acceso", "restablece"),
            ("acceso", "priv", "bajo")
        ]

        node_map = {node.key: node for node in self.nodes}
        for k1, k2, label in connections:
            n1 = node_map[k1]
            n2 = node_map[k2]

            # Dibujar línea en canvas
            y1_line = n1.y + n1.h / 2 if n1.y < n2.y else n1.y - n1.h / 2
            y2_line = n2.y - n2.h / 2 if n1.y < n2.y else n2.y + n2.h / 2

            self.canvas.create_line(n1.x, y1_line, n2.x, y2_line, fill=COLOR_TEXT_MUTED, arrow="last", width=1.5)
            self.pil_draw.line([(int(n1.x), int(y1_line)), (int(n2.x), int(y2_line))], fill="#94a3b8", width=2)

            # Etiqueta
            lx = (n1.x + n2.x) / 2
            ly = (n1.y + n2.y) / 2

            # Canvas label con fondo manual
            txt_id = self.canvas.create_text(lx, ly, text=label, font=("Segoe UI", 7, "italic"), fill=COLOR_TEXT_MUTED)
            bbox = self.canvas.bbox(txt_id)
            if bbox:
                bx1, by1, bx2, by2 = bbox
                rect_id = self.canvas.create_rectangle(bx1 - 3, by1 - 1, bx2 + 3, by2 + 1, fill="#ffffff", outline="")
                self.canvas.tag_lower(rect_id, txt_id)

            # PIL label
            lbl_w = self.pil_draw.textlength(label, font=self.pil_font_body)
            self.pil_draw.rectangle([int(lx - lbl_w / 2 - 3), int(ly - 6), int(lx + lbl_w / 2 + 3), int(ly + 6)],
                                    fill="#ffffff")
            self.pil_draw.text((int(lx - lbl_w / 2), int(ly - 5)), label, font=self.pil_font_body, fill="#94a3b8")

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
                text="Haz clic en cualquier nodo para ver su descripción, requerimientos de seguridad e implicación técnica.")
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
            initialfile="mapa_conceptual.png",
            title="Guardar Mapa Conceptual"
        )
        if filepath:
            try:
                self.pil_img.save(filepath, "PNG")
                messagebox.showinfo("Exportación Exitosa", f"Guardado correctamente en:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ConceptualMapApp(root)
    root.mainloop()