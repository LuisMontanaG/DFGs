from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate

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

                # Update dropdown the options which are the good_k values
                # options = [{"label": str(i), "value": i} for i in good_k]

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

        # @self.app.callback(
        #     Output('graph-container', 'children', allow_duplicate=True),
        #     Input('k-dropdown', 'value'),
        #     State("dataset-selector", "value"),
        #     prevent_initial_call=True,
        # )
        # def update_graphs(k_value, dataset_name):
        #     if not dataset_name or k_value is None:
        #         raise PreventUpdate
        #
        #     graphs = self.graph_builder.get_graphs(int(k_value))
        #
        #     return graphs
