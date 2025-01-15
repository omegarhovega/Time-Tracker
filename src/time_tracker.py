import tkinter as tk
from datetime import datetime

from src.models.data_classes import Colors, Dimensions
from src.sections.date_navigation import DateNavigationBar
from src.sections.time_blocks import TimeBlocksSection
from src.sections.top_tasks import TopTasksSection


class TimeManagementApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Time Tracker")

        # Initialize configuration classes
        self.colors = Colors()
        self.dims = Dimensions()

        # Set exact window size
        total_width = sum(self.dims.CANVAS_WIDTH.values())
        self.window.geometry(f"{total_width}x{self.dims.TOTAL_HEIGHT}")
        self.window.resizable(False, False)

        # Configure window background
        self.window.configure(bg=self.colors.BACKGROUND[1])

        # Configure grid weights
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(0, minsize=self.dims.NAV_HEIGHT)
        self.window.grid_rowconfigure(
            1, minsize=self.dims.TOP_TASKS_HEIGHT
        )  # Top tasks
        self.window.grid_rowconfigure(
            2, minsize=self.dims.TIME_BLOCKS_HEIGHT
        )  # Time blocks (includes title and canvas)

        self.current_date = datetime.now().date()

        # Initialize sections
        self.date_navigation = DateNavigationBar(
            parent=self.window,
            initial_date=self.current_date,
            on_date_change=self.handle_date_change,
        )
        self.date_navigation.grid(row=0, column=0, sticky="ew")

        self.top_tasks = TopTasksSection(
            parent=self.window, current_date=self.current_date
        )
        self.top_tasks.grid(row=1, column=0, sticky="ew")

        self.time_blocks = TimeBlocksSection(
            parent=self.window, current_date=self.current_date
        )
        self.time_blocks.grid(
            row=2, column=0, sticky="nsew"
        )  # Changed from row=2 to match configuration

    def handle_date_change(self, new_date):
        """Handle date changes and update all sections"""
        self.current_date = new_date
        self.top_tasks.load_tasks(new_date)
        self.time_blocks.load_blocks(new_date)

    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    app = TimeManagementApp()
    app.run()
