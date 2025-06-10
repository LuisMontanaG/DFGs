import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from utils.colours import ColorUtils
from dash import dcc
import math

class GraphBuilder:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.event_type_colors = {}
        self.event_types = {}

    def get_event_type_colors(self):
        self.event_types = self.data_manager.get_event_types()
        for key, value in self.event_types.items():
            index = int(key) - 1
            self.event_type_colors[value] = ColorUtils.get_color(index)

    def get_graphs(self, k):
        self.get_event_type_colors()
        # Get clustering data for the given k
        clustering_data = self.data_manager.get_clustering(k)

        # Build a cytoscape graph per key in clustering_data
        graphs = []
        for i, (key, value) in enumerate(clustering_data.items()):  # Use enumerate to get sequential index
            graphs.append(self.create_graph(i, value))  # Pass sequential index instead of cluster_id

        rows = []
        cluster_count = 1
        for i, graph in enumerate(graphs):
            # Create a row with the cluster title and fullscreen button
            title_row = dbc.Row([
                dbc.Col([
                    dbc.Container([
                        dcc.Markdown(f"### Cluster {cluster_count}", 
                                   style={"textAlign":"center", "margin": "0", "display": "inline-block"}),
                        dbc.Button(
                            "Fullscreen",
                            id={"type": "fullscreen-btn", "index": i},
                            color="link",
                            size="sm",
                            title="View in fullscreen",
                            style={
                                "marginLeft": "10px",
                                "padding": "2px 6px", 
                                "fontSize": "16px",
                                "verticalAlign": "middle"
                            }
                        )
                    ], style={
                        "display": "flex", 
                        "alignItems": "center",
                        "justifyContent": "center"
                    })
                ], width=12)
            ], className="mb-2")
            rows.append(title_row)
            
            cluster_count += 1
            
            # Create the graph row
            row = dbc.Row(
                dbc.Col(graph, width=12),
                className="mb-4"
            )
            rows.append(row)
            
        return rows

    def create_graph(self, cluster_id, ids):
        # Get unique sequences
        unique_sequences = self.data_manager.get_unique_sequences()
        acronyms = self.data_manager.get_event_types_acronyms()
        # Get sequences to create nodes and edges
        nodes_dict = {}
        edges_dict = {}
        for id in ids:
            # Get the sequence for the given id, where id_uniqueSeq == id
            sequence = unique_sequences.loc[unique_sequences['id_uniqueSeq'] == int(id), 'sequence'].values[0]
            frequency = unique_sequences.loc[unique_sequences['id_uniqueSeq'] == int(id), 'frequency'].values[0]
            sequence = sequence.split('-')
            # Get node frequencies
            for event in sequence:
                if event not in nodes_dict:
                    nodes_dict[event] = frequency
                else:
                    nodes_dict[event] += frequency
            # Get edges
            for i in range(len(sequence) - 1):
                edge = (sequence[i], sequence[i + 1])
                if edge not in edges_dict:
                    edges_dict[edge] = frequency
                else:
                    edges_dict[edge] += frequency

        # Change the node dictionary keys to their mapping in event_types
        nodes_dict = {self.event_types[int(event)]: freq for event, freq in nodes_dict.items()}
        # Change the edge dictionary keys to their mapping in event_types
        edges_dict = {(self.event_types[int(edge[0])], self.event_types[int(edge[1])]): freq for edge, freq in edges_dict.items()}

        # Calculate min and max frequencies for dynamic scaling
        node_frequencies = list(nodes_dict.values())
        edge_weights = list(edges_dict.values())

        min_node_freq = min(node_frequencies) if node_frequencies else 1
        max_node_freq = max(node_frequencies) if node_frequencies else 1
        min_edge_weight = min(edge_weights) if edge_weights else 1
        max_edge_weight = max(edge_weights) if edge_weights else 1

        # Use logarithmic scaling for better distribution
        log_min_node = math.log10(max(min_node_freq, 1))
        log_max_node = math.log10(max_node_freq)
        log_min_edge = math.log10(max(min_edge_weight, 1))
        log_max_edge = math.log10(max_edge_weight)

        # Create nodes and edges for cytoscape
        nodes = []
        for event, freq in nodes_dict.items():
            color = self.event_type_colors[event]
            log_freq = math.log10(max(freq, 1))
            nodes.append({
                "data": {
                    "id": event,
                    "label": acronyms[event],
                    "frequency": freq,
                    "log_frequency": log_freq,
                    "color": color
                },
            })

        edges = []
        for edge, freq in edges_dict.items():
            log_weight = math.log10(max(freq, 1))
            edges.append({
                "data": {
                    "source": edge[0],
                    "target": edge[1],
                    "weight": freq,  # Keep original for tooltip
                    "log_weight": log_weight,  # Add logarithmic value for sizing
                }
            })

        elements = nodes + edges

        # Create the stylesheet with class-based coloring for each event type
        stylesheet = [
            {
                "selector": "node",
                "style": {
                    "label": "data(label)",
                    "color": "#000000",
                    "background-color": "data(color)",
                    "text-valign": "center",
                    "text-halign": "center",
                    "width": f"mapData(log_frequency, {log_min_node}, {log_max_node}, 20, 80)",
                    "height": f"mapData(log_frequency, {log_min_node}, {log_max_node}, 20, 80)",
                    "font-size": f"mapData(log_frequency, {log_min_node}, {log_max_node}, 12, 16)"
                },
            },
            {
                "selector": "edge",
                "style": {
                    "curve-style": "bezier",
                    "width": f"mapData(log_weight, {log_min_edge}, {log_max_edge}, 1, 8)",
                    "line-color": "#ccc",
                    "target-arrow-color": "#ccc",
                    "target-arrow-shape": "triangle",
                },
            },
        ]

        return cyto.Cytoscape(
            id={"type": "graph", "index": cluster_id},
            elements=elements,
            layout={"name": "dagre", "rankDir": "LR"},
            style={"width": "100%", "height": "200px"},
            stylesheet=stylesheet,
        )