import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from utils.colours import ColorUtils
from dash import dcc, html


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
                                "margin-left": "10px", 
                                "padding": "2px 6px", 
                                "font-size": "16px",
                                "vertical-align": "middle"
                            }
                        )
                    ], style={
                        "display": "flex", 
                        "align-items": "center", 
                        "justify-content": "center"
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

        # Create nodes and edges for cytoscape
        nodes = []
        for event, freq in nodes_dict.items():
            color = self.event_type_colors[event]
            nodes.append({
                "data": {
                    "id": event,
                    "label": acronyms[event],
                    "frequency": freq,
                    "color": color
                },
            })

        edges = [{"data": {"source": edge[0], "target": edge[1], "weight": freq}} for edge, freq in edges_dict.items()]
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
                    "width": "mapData(frequency, 0, 100, 20, 60)",
                    "height": "mapData(frequency, 0, 100, 20, 60)",
                },
            },
            {
                "selector": "edge",
                "style": {
                    "curve-style": "bezier",
                    "width": "mapData(weight, 0, 100, 1, 5)",
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