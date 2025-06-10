import dash_bootstrap_components as dbc
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
                updatemode="mouseup",
                className="dbc",
            )
        ], width=9)
        
        graph_container = dbc.Container(
            id="graph-container",
            className="dbc"
        )

        # Modal tooltip
        modal_tooltip_div = dbc.Container(
            id="modal-tooltip",
            children="",
            style={
                "color": "black",
                "display": "block",
                "minHeight": "30px",
                "lineHeight": "30px",
            }
        )

        # Initialize modal in the layout
        fullscreen_modal = dbc.Modal([
            dbc.ModalHeader([
                dbc.ModalTitle(id="modal-title", children=""),
            ]),
            dbc.ModalBody([
                modal_tooltip_div,
                dbc.Container(
                    id="modal-graph-container",
                    style={"height": "80vh", "width": "80vh", "padding": "20px"},
                    children=[]
                )
            ]),
        ],
        id="fullscreen-modal",
        size="xl",
        is_open=False,)


        tooltip_div = dbc.Container(
            id="tooltip",
            children="",
            style={
                "position": "fixed",
                "bottom": "10px",
                "right": "0px",
                "zIndex": "1000",
                "color": "black",
                "display": "block",
                "minHeight": "30px",
                "lineHeight": "30px",
            }
        )

        # Add interval component for tooltip auto-hide
        tooltip_interval = dcc.Interval(
            id="tooltip-interval",
            interval=5000,  # 2 seconds
            n_intervals=0,
            disabled=True  # Start disabled
        )

        # Add interval component for modal tooltip auto-hide
        modal_tooltip_interval = dcc.Interval(
            id="modal-tooltip-interval",
            interval=5000,  # 5 seconds
            n_intervals=0,
            disabled=True  # Start disabled
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
                tooltip_div,  # Add tooltip to layout
            ),
            dbc.Row(
                graph_container
            ),
            tooltip_interval,
            modal_tooltip_interval,
            fullscreen_modal  # Add modal directly to layout
        ], fluid=True)