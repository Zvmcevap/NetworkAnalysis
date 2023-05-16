import time

from classes.StringManager import StringManager
from classes.GraphManager import GraphManager


def main():
    gm = GraphManager()
    ui = StringManager(gm)

    wrong_command = False
    while True:  # Main Loop
        options = []
        if gm.current_graph is not None:
            options += ["d-graph details"]
        options += ["l-load_graph", "g-generate graph", "q-quit"]
        ui.print(
            sentence="",
            options=options,
            wrong_command=wrong_command
        )
        command = input("Enter command: ")
        if command == "q":
            return

        elif command == "l":
            wrong_command = False
            if ui.load_graph():
                ui.graph_analysis()

        elif command == "g":
            wrong_command = False
            if ui.generate_graph():
                ui.graph_analysis()

        # Graph loaded
        elif gm.current_graph and command == "d":
            wrong_command = False
            ui.graph_analysis()

        else:
            wrong_command = True


if __name__ == "__main__":
    main()
