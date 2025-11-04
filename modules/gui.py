from tkinter import Tk, Canvas, PhotoImage, scrolledtext      # added scrolledtext for log window
from pathlib import Path
from PIL import Image, ImageTk
from modules.reference import process_reference
from modules.test_input import process_test_input
from modules.comparison import process_comparison
import sys
import threading                                              # so UI doesn’t freeze


class Gui:
    def __init__(self):
        """Initialize the window and canvas structure — no UI content yet."""
        self.window = Tk()
        self.window.geometry("1000x629")
        self.window.configure(bg="#EAF4FF")

        # Create canvas
        self.canvas = Canvas(
            self.window,
            bg="#EAF4FF",
            height=629,
            width=1380,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        # --- 🪶 NEW: Create log text window at bottom ---
        self.log_area = scrolledtext.ScrolledText(
            self.window,
            width=120,
            height=10,
            state='disabled',
            wrap='word',
            bg="#F4F7FB"
        )
        self.log_area.place(x=40, y=100)  # adjust position as needed

        # Redirect console output (print statements)
        sys.stdout = self
        sys.stderr = self

        # Keep references for images
        self.avatar_images = []
        self.button_images = []

    # ---------- LOGGING ----------
    def write(self, message: str):
        """Redirected stdout/stderr handler."""
        self.log_area.config(state='normal')
        self.log_area.insert('end', message)
        self.log_area.see('end')  # auto-scroll
        self.log_area.config(state='disabled')

    def flush(self):
        """Required for sys.stdout redirection (no-op)."""
        pass

    # ---------- BUILD PHASE ----------
    def build_gui(self):
        self.add_title()
        self.insert_avatars()
        self.insert_center_button()

    def add_title(self):
        self.canvas.create_text(
            690, 10,
            anchor="n",
            text="TPH, coming to take over the world!",
            fill="#1378e8",
            font=("Inter", 20, "bold")
        )

    # ---------- ASSET HANDLING ----------
    def relative_to_assets(self, folder: str, filename: str) -> str:
        base_path = Path(__file__).resolve().parent.parent
        asset_path = base_path / "assets" / folder
        return str(asset_path / filename)

    # ---------- AVATARS ----------
    def insert_avatars(self):
        avatar_filenames = [
            "Sudheep.PNG", "Vetri.PNG", "Vinoth.PNG", "Elgine.PNG",
            "Farrah.PNG", "Harish.PNG", "Rene.PNG", "Ram.PNG", "Sanja.PNG"
        ]
        start_x, x_spacing, y_position = 90.0, 150.0, 512.0

        for i, filename in enumerate(avatar_filenames):
            path = self.relative_to_assets("Pictures", filename)
            original = Image.open(path)
            resized = original.resize((160, 160))
            avatar = ImageTk.PhotoImage(resized)
            self.avatar_images.append(avatar)

            x_position = start_x + i * x_spacing
            self.canvas.create_image(x_position, y_position, image=avatar, anchor="center")

    # ---------- BUTTON ----------
    def insert_center_button(self):
        canvas_width, canvas_height = int(self.canvas["width"]), int(self.canvas["height"])
        path = self.relative_to_assets("frame0", "button_3.png")
        print(f"Loading button image: {path}")

        original = Image.open(path)
        resized = original.resize((223, 79))
        button_img = ImageTk.PhotoImage(resized)
        self.button_images.append(button_img)

        x_center, y_center = canvas_width // 2, canvas_height // 2
        button_id = self.canvas.create_image(x_center, y_center, image=button_img, anchor="center")

        # Bind button click event
        self.canvas.tag_bind(button_id, "<Button-1>", lambda e: self.start_tasks_thread())

    # ---------- RUN MODULES ----------
    def start_tasks_thread(self):
        """Run modules in background thread so GUI stays responsive."""
        threading.Thread(target=self.on_button_click, daemon=True).start()

    def on_button_click(self):
        """Execute automation modules sequentially."""
        print("🟢 button_3 clicked — executing automation tasks...\n")
        try:
            print("▶ Running reference module...")
            process_reference()
            print("✅ Reference module completed successfully.\n")

            print("▶ Running test_input module...")
            process_test_input()
            print("✅ Test_input module completed successfully.\n")

            print("▶ Running comparison module...")
            process_comparison()
            print("✅ Comparison module completed successfully.\n")

            print("🎯 All processes executed successfully.\n")
        except Exception as e:
            print(f"❌ Error executing modules: {e}\n")

    # ---------- MAINLOOP ----------
    def run(self):
        self.window.resizable(True, True)
        self.window.mainloop()
