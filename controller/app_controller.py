from dash import Dash
import dash_bootstrap_components as dbc

from model.data_manager import DataManager
from view.graph_builder import GraphBuilder
from view.layout_manager import LayoutManager
from controller.callbacks_manager import CallbacksManager



class AppController:

    def __init__(self):
        self.app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.data_manager = DataManager()
        self.layout_manager = LayoutManager(self.data_manager)
        self.graph_builder = GraphBuilder(self.data_manager)
        self.callbacks = CallbacksManager(self.app, self.data_manager, self.graph_builder)
        self.callbacks.register_callbacks()

        self.app.layout = self.layout_manager.get_layout()

