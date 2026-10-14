import matplotlib.pyplot as plt
import networkx as nx


def crear_mapa_conceptual():
    # Crear grafo dirigido
    G = nx.DiGraph()

    # Definir conexiones (Origen, Destino, Relación)
    relaciones = [
        ('Circuitería E/S', 'Multiplexación GPIO', 'se implementa en'),
        ('Circuitería E/S', 'Lógica DeMorgan', 'se basa en'),
        ('Circuitería E/S', 'Tolerancia a Fallos', 'garantiza'),
        ('Circuitería E/S', 'Salidas Configurables', 'utiliza'),
        ('Multiplexación GPIO', 'Periféricos (UART/SPI)', 'reutiliza pines para'),
        ('Lógica DeMorgan', 'Símbolos Duales', 'representa con'),
        ('Tolerancia a Fallos', 'Canales de Respaldo', 'activa ante fallo'),
        ('Salidas Configurables', 'Tri-State', 'permite bus compartido'),
        ('Salidas Configurables', 'Open-Drain', 'requiere pull-up'),
    ]

    for origen, destino, label in relaciones:
        G.add_edge(origen, destino, label=label)

    # Disposición jerárquica
    pos = {
        'Circuitería E/S': (0, 2),
        'Multiplexación GPIO': (-3, 1),
        'Lógica DeMorgan': (-1, 1),
        'Tolerancia a Fallos': (1, 1),
        'Salidas Configurables': (3, 1),
        'Periféricos (UART/SPI)': (-3, 0),
        'Símbolos Duales': (-1, 0),
        'Canales de Respaldo': (1, 0),
        'Tri-State': (2.3, 0),
        'Open-Drain': (3.7, 0)
    }

    plt.figure(figsize=(14, 8))

    # Dibujar nodos (usando node_shape en vez de shape)
    nx.draw_networkx_nodes(G, pos, node_color='#2B5B84', node_size=3500, node_shape='s')
    nx.draw_networkx_labels(G, pos, font_color='white', font_size=8, font_weight='bold')
    nx.draw_networkx_edges(G, pos, edge_color='#555555', arrows=True, arrowsize=15, min_source_margin=15,
                           min_target_margin=15)

    # Dibujar etiquetas de las aristas
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7)

    plt.title("Mapa Conceptual: Circuitería Alternativa E/S", fontsize=14, fontweight='bold')
    plt.axis('off')
    plt.tight_layout()

    # Guardar y mostrar imagen
    plt.savefig("mapa_conceptual_es.png", dpi=300)
    plt.show()


if __name__ == '__main__':
    crear_mapa_conceptual()