from controller.app_controller import AppController
import dash_cytoscape as cyto

def main():
    """
    Application entry point.
    Creates the app controller and runs the Dash server.
    """
    cyto.load_extra_layouts()
    controller = AppController()
    controller.app.run(debug=True)

if __name__ == "__main__":
    main()