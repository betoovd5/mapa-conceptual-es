import matplotlib.pyplot as plt
import networkx as nx

# 1. Creación del mapa conceptual (Grafo Dirigido)
G = nx.DiGraph()

# 2. Definición de la estructura y relaciones (Origen -> Destino)
relaciones = [
    # Conexiones desde el Tema Central
    ("SISTEMAS DE\nCOMUNICACIÓN", "TIPOS"),
    ("SISTEMAS DE\nCOMUNICACIÓN", "FUNCIONAMIENTO"),
    ("SISTEMAS DE\nCOMUNICACIÓN", "CARACTERÍSTICAS"),
    ("SISTEMAS DE\nCOMUNICACIÓN", "MODO DE\nCOMUNICACIÓN"),
    # Subnodos de TIPOS
    ("TIPOS", "Simplex:\nUnidireccional (Ej: TV, Radio)"),
    (
        "TIPOS",
        "Half-Duplex:\nBidireccional alternado\n(Ej: Walkie-Talkie)",
    ),
    (
        "TIPOS",
        "Full-Duplex:\nBidireccional simultáneo\n(Ej: Llamada telefónica)",
    ),
    # Subnodos de FUNCIONAMIENTO
    (
        "FUNCIONAMIENTO",
        "1. Emisor:\nCodifica y envía\nel mensaje",
    ),
    (
        "FUNCIONAMIENTO",
        "2. Canal / Medio:\nTransporta la señal\n(con posible ruido)",
    ),
    (
        "FUNCIONAMIENTO",
        "3. Receptor:\nRecibe y decodifica\nel mensaje",
    ),
    # Subnodos de CARACTERÍSTICAS
    (
        "CARACTERÍSTICAS",
        "Ancho de Banda:\nCapacidad máxima de\ntransmisión de datos",
    ),
    (
        "CARACTERÍSTICAS",
        "Latencia:\nTiempo de retardo en\nllegar el paquete",
    ),
    (
        "CARACTERÍSTICAS",
        "Fiabilidad / SNR:\nRelación señal-ruido\ny tasa de errores",
    ),
    # Subnodos de MODO DE COMUNICACIÓN
    (
        "MODO DE\nCOMUNICACIÓN",
        "Guiados (Con cable):\n- Par trenzado (Ethernet)\n- Cable Coaxial\n- Fibra Óptica",
    ),
    (
        "MODO DE\nCOMUNICACIÓN",
        "No Guiados (Inalámbricos):\n- Ondas de Radio (Wi-Fi)\n- Microondas\n- Infrarrojos",
    ),
]

G.add_edges_from(relaciones)

# 3. Asignación de colores por categorías para diferenciar visualmente
color_map = []
for node in G:
    if node == "SISTEMAS DE\nCOMUNICACIÓN":
        color_map.append("#2C3E50")  # Azul Oscuro (Principal)
    elif node in [
        "TIPOS",
        "FUNCIONAMIENTO",
        "CARACTERÍSTICAS",
        "MODO DE\nCOMUNICACIÓN",
    ]:
        color_map.append("#2980B9")  # Azul Medio (Categorías)
    else:
        color_map.append("#AED6F1")  # Azul Claro (Información Detallada)

# 4. Configuración del diseño del diagrama
plt.figure(figsize=(16, 10))
pos = nx.spring_layout(G, k=0.8, seed=42)  # Distribución de los nodos

# Dibujar nodos y conexiones
nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=5500, alpha=0.9)
nx.draw_networkx_edges(
    G, pos, edge_color="#7F8C8D", arrows=True, arrowsize=18, width=1.5
)

# Renderizar los textos dentro de los nodos
nx.draw_networkx_labels(
    G,
    pos,
    font_size=7,
    font_family="sans-serif",
    font_weight="bold",
    font_color="black",
)

# Personalización de la ventana de diálogo
plt.title("Mapa Conceptual: Sistemas de Comunicación", fontsize=14, fontweight="bold")
plt.axis("off")  # Ocultar ejes de coordenadas
plt.tight_layout()

# Mostrar el gráfico interactivo
plt.show()