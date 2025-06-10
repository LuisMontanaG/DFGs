from dash import Dash, html, dcc, Input, Output, State, ALL, callback_context, no_update
from dash.exceptions import PreventUpdate
import dash_cytoscape as cyto
import json


class CallbacksManager:

    def __init__(self, app, data_manager, graph_builder):
        self.app = app
        self.data_manager = data_manager
        self.graph_builder = graph_builder

    def register_callbacks(self):

        @self.app.callback(
            Output("k-slider", "max"),
            Output("k-slider", "value"),
            Output("k-slider", "min"),
            Output('k-slider', 'marks'),
            Output('graph-container', 'children'),
            Input("load-dataset-button", "n_clicks"),
            State("dataset-selector", "value"),
        )
        def load_dataset(n_clicks, dataset_name):
            if n_clicks > 0:
                # Load data
                self.data_manager.load_dataset(dataset_name)
                self.data_manager.load_files()

                # Update slider
                max_k = self.data_manager.get_max_k()
                min_k = self.data_manager.get_min_k()
                k = self.data_manager.get_best_k()
                good_k = self.data_manager.get_good_k()
                # Create marks based on good_k
                marks = {i: "" for i in good_k}
                # Set marks labels for min and max k
                marks[max_k] = str(max_k)
                marks[min_k] = str(min_k)

                # Update graph container
                graphs = self.graph_builder.get_graphs(k)

                return max_k, k, min_k, marks, graphs
            else:
                raise PreventUpdate

        @self.app.callback(
            Output('graph-container', 'children', allow_duplicate=True),
            Input('k-slider', 'value'),
            State("dataset-selector", "value"),
            prevent_initial_call=True,
        )
        def update_graphs(k_value, dataset_name):
            if not dataset_name or k_value is None:
                raise PreventUpdate

            graphs = self.graph_builder.get_graphs(k_value)

            return graphs

        @self.app.callback(
            [Output("fullscreen-modal", "is_open"),
             Output("modal-title", "children"),
             Output("modal-graph-container", "children")],
            [Input({"type": "fullscreen-btn", "index": ALL}, "n_clicks")],
             State("graph-container", "children"),
            prevent_initial_call=True
        )
        def handle_fullscreen_modal(fullscreen_clicks, graph_rows):
            ctx = callback_context
            
            # Prevent execution if no trigger or if fullscreen_clicks is empty/None
            if not ctx.triggered or not fullscreen_clicks:
                raise PreventUpdate
            
            # Check if any button was actually clicked (not just initial load)
            trigger_value = ctx.triggered[0]['value']
            if trigger_value is None or trigger_value == 0:
                raise PreventUpdate
            
            # Get the triggered input ID
            trigger_id = ctx.triggered[0]['prop_id']
            
            # Parse the triggered button to get the index
            if "fullscreen-btn" in trigger_id:
                # Extract the index from the triggered ID
                # The trigger_id looks like: {"index":0,"type":"fullscreen-btn"}.n_clicks
                trigger_id_clean = trigger_id.replace('.n_clicks', '')
                try:
                    trigger_dict = json.loads(trigger_id_clean)
                    clicked_index = trigger_dict['index']
                    
                    if graph_rows and clicked_index is not None:
                        # Calculate the graph row index (titles are at even indices, graphs at odd indices)
                        graph_row_index = (clicked_index * 2) + 1
                        
                        if graph_row_index < len(graph_rows):
                            # Extract the original graph data
                            graph_row = graph_rows[graph_row_index]
                            
                            # Navigate through the nested structure to get the graph
                            try:
                                # graph_row -> props -> children -> props -> children (the actual graph)
                                graph_data = graph_row['props']['children']['props']['children']
                                
                                # Extract graph properties from the dict representation
                                graph_id = graph_data['props']['id']
                                elements = graph_data['props']['elements']
                                layout = graph_data['props']['layout']
                                stylesheet = graph_data['props']['stylesheet']
                                
                                # Create the fullscreen version with larger dimensions
                                fullscreen_graph = cyto.Cytoscape(
                                    id={"type": "fullscreen-graph", "index": clicked_index},
                                    # Use pattern matching format
                                    elements=elements,
                                    layout=layout,
                                    stylesheet=stylesheet,
                                    style={"width": "100%", "height": "100%"}
                                )

                                modal_title = f"Cluster {clicked_index + 1}"
                                return True, modal_title, fullscreen_graph
                                
                            except (KeyError, TypeError) as e:
                                print(f"Error extracting graph data: {e}")
                                raise PreventUpdate
                                
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error parsing trigger ID: {e}")
                    raise PreventUpdate
            
            raise PreventUpdate

        @self.app.callback(
            [Output("tooltip", "children"),
             Output("tooltip-interval", "disabled")],
            [Input({"type": "graph", "index": ALL}, "mouseoverNodeData"),
             Input({"type": "graph", "index": ALL}, "mouseoverEdgeData")],
            prevent_initial_call=True
        )
        def display_tooltip(node_data_list, edge_data_list):
            ctx = callback_context
            if not ctx.triggered:
                return [" ", True]

            # Get the most recent trigger
            trigger_id = ctx.triggered[0]['prop_id']
            
            # Extract the graph index from the trigger ID
            # Example trigger_id: '{"index":0,"type":"graph"}.mouseoverNodeData'
            import json
            try:
                # Remove the property part to get just the component ID
                component_id_str = trigger_id.split('.')[0]
                component_id = json.loads(component_id_str)
                triggered_graph_index = component_id['index']
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(f"Error parsing trigger ID: {e}")
                return [" ", True]
            
            # Check if the trigger was from a node mouseover
            if "mouseoverNodeData" in trigger_id:
                # Only check the data from the triggered graph
                if triggered_graph_index < len(node_data_list) and node_data_list[triggered_graph_index]:
                    node_data = node_data_list[triggered_graph_index]
                    tooltip_text = f"{node_data['id']}, Frequency: {node_data['frequency']}"
                    return [tooltip_text, False]  # Show tooltip and enable interval
            
            # Check if the trigger was from an edge mouseover
            elif "mouseoverEdgeData" in trigger_id:
                # Only check the data from the triggered graph
                if triggered_graph_index < len(edge_data_list) and edge_data_list[triggered_graph_index]:
                    edge_data = edge_data_list[triggered_graph_index]
                    tooltip_text = f"{edge_data['source']} → {edge_data['target']}, Weight: {edge_data['weight']}"
                    return [tooltip_text, False]  # Show tooltip and enable interval

            return [" ", True]  # Hide tooltip and disable interval

        # Hide tooltip after interval
        @self.app.callback(
            [Output("tooltip", "children", allow_duplicate=True),
             Output("tooltip-interval", "disabled", allow_duplicate=True)],
            [Input("tooltip-interval", "n_intervals")],
            prevent_initial_call=True
        )
        def hide_tooltip_after_delay(n_intervals):
            if n_intervals > 0:
                return [" ", True]  # Hide tooltip and disable interval
            return [" ", True]

        # Modal tooltip callbacks - listen to fullscreen graphs
        @self.app.callback(
            [Output("modal-tooltip", "children"),
             Output("modal-tooltip-interval", "disabled")],
            [Input({"type": "fullscreen-graph", "index": ALL}, "mouseoverNodeData"),
             Input({"type": "fullscreen-graph", "index": ALL}, "mouseoverEdgeData")],
            prevent_initial_call=True
        )
        def display_modal_tooltip(node_data_list, edge_data_list):
            ctx = callback_context
            if not ctx.triggered:
                return [" ", True]

            trigger_id = ctx.triggered[0]['prop_id']
            
            # Check if the trigger was from a node mouseover
            if "mouseoverNodeData" in trigger_id:
                # Always use index 0 since there's only one graph in the modal
                if node_data_list and node_data_list[0]:
                    node_data = node_data_list[0]
                    tooltip_text = f"{node_data['id']}, Frequency: {node_data['frequency']}"
                    return [tooltip_text, False]
            
            # Check if the trigger was from an edge mouseover
            elif "mouseoverEdgeData" in trigger_id:
                # Always use index 0 since there's only one graph in the modal
                if edge_data_list and edge_data_list[0]:
                    edge_data = edge_data_list[0]
                    tooltip_text = f"{edge_data['source']} → {edge_data['target']}, Weight: {edge_data['weight']}"
                    return [tooltip_text, False]

            return [" ", True]

        # Hide modal tooltip after interval
        @self.app.callback(
            [Output("modal-tooltip", "children", allow_duplicate=True),
             Output("modal-tooltip-interval", "disabled", allow_duplicate=True)],
            [Input("modal-tooltip-interval", "n_intervals")],
            prevent_initial_call=True
        )
        def hide_modal_tooltip_after_delay(n_intervals):
            if n_intervals > 0:
                return [" ", True]
            return [" ", True]