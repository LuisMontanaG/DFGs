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
                updatemode="drag",
                className="dbc",
            )
        ], width=9)
        
        graph_container = dbc.Container(
            id="graph-container",
            className="dbc"
        )

        # Modal tooltip
        modal_tooltip_div = html.Div(
            id="modal-tooltip",
            children=" ",
            style={
                "color": "black",
                "padding": "8px",
                "border-radius": "4px",
                "font-size": "12px",
                "pointer-events": "none",
                "z-index": "2000",  # Higher z-index for modal
                "display": "block",
                "white-space": "pre-line"
            }
        )

        # Initialize modal in the layout
        fullscreen_modal = dbc.Modal([
            dbc.ModalHeader([
                dbc.ModalTitle(id="modal-title", children=""),
            ]),
            dbc.ModalBody([
                modal_tooltip_div,  # Add modal tooltip inside modal body
                html.Div(
                    id="modal-graph-container",
                    style={"height": "75vh", "padding": "10px"},
                    children=[]
                )
            ]),
        ],
        id="fullscreen-modal",
        size="xl",
        is_open=False,
        style={"max-width": "95vw"})


        tooltip_div = html.Div(
            id="tooltip",
            children=" ",
            style={
                "color": "black",
                "padding": "8px",
                "border-radius": "4px",
                "font-size": "12px",
                "pointer-events": "none",
                "z-index": "1000",
                "display": "block",
                "white-space": "pre-line"
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