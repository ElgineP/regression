from modules.gui import Gui


if __name__ == "__main__":
    app = Gui()          # Build window structure
    app.build_gui()      # Add all elements (avatars, buttons, etc.)
    app.run()            # Launch the event loop
