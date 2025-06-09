import dash_bootstrap_components as dbc
from click import style
from dash import html, dcc


class LayoutManager:

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def get_layout(self):
        dropdown_dataset_col = dbc.Col([
            html.Label("Select Dataset: ", style={"fontSize": "16px", "marginBottom": "5px", "fontWeight": "bold"}),
            dcc.Dropdown(
                id="dataset-selector",
                options=self.data_manager.get_available_datasets(),
                placeholder="Select a dataset",
                clearable=False,
                style={"width": "200px"},
                className="dbc",
            ),
        ], width=2)
        button_load_col = dbc.Col([
            dbc.Button("Load", id="load-dataset-button", n_clicks=0,
                       style={"marginTop": "30px", "marginLeft": "-50px", 'fontSize': '14px'}),
        ], width=1)
        k_slider_col = dbc.Col([
            html.Label("Number of Clusters", style={"fontSize": "16px", "marginBottom": "5px", "fontWeight": "bold"}),
            dcc.Slider(
                id="k-slider",
                min=1,
                max=10,
                step=1,
                value=1,
                marks={i: str(i) for i in range(1, 11, 1)},  # Example marks
                tooltip={"placement": "bottom", "always_visible": True},
                included=False,
                updatemode="drag",
                className="dbc",
            )
        ], width=9)
        # k_dropdown_col = dbc.Col([
        #     html.Label("Number of Clusters: ",
        #                style={"fontSize": "16px", "marginBottom": "5px", "fontWeight": "bold"}),
        #     dcc.Dropdown(
        #         id="k-dropdown",
        #         options=[
        #             {"label": str(i), "value": i} for i in range(1, 11)
        #         ],  # Example options
        #         placeholder="Select number of clusters",
        #         clearable=False,
        #         style={"width": "200px"},
        #         className="dbc",
        #     ),
        # ], width=2)
        graph_container = dbc.Container(
            id="graph-container",
            className="dbc"
        )

        return dbc.Container([
            dbc.Row(
                dcc.Markdown("# DFG", style={"textAlign": "center", "marginBottom": "10px", "marginTop": "5px"})
            ),
            dbc.Row([
                dropdown_dataset_col,
                button_load_col,
                k_slider_col
            ]),
            dbc.Row(
                graph_container
            )
        ], fluid=True)
