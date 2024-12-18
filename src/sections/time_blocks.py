import tkinter as tk
from tkinter import Toplevel, StringVar, OptionMenu, messagebox
from datetime import datetime, timedelta
from src.models.data_classes import Task, Colors, Dimensions, UIConfig
from src.utils.tooltip import TooltipManager
from src.data_manager import DataManager
from typing import Optional

class TimeBlocksSection(tk.Frame):
    def __init__(self, parent, current_date):
        super().__init__(parent)
        
        # Store reference to main window
        self.window = parent.winfo_toplevel()
        
        # Initialize configuration classes
        self.dims = Dimensions()
        self.colors = Colors()
        self.config = UIConfig()
        self.data_manager = DataManager()
        
        # Initialize tracking attributes
        self.current_date = current_date
        self.tasks = []
        self.canvases = {}
        
        # Initialize interaction state
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.active_task = None
        self.drag_start_y = 0
        self.original_start_time = 0
        self.original_end_time = 0
        self.drag_offset = 0
        
        # Initialize scheduled update reference
        self._scheduled_update = None
        
        # Initialize hour positions
        self.HOUR_POSITIONS = [
            (hour * self.dims.HOUR_HEIGHT, self.colors.BACKGROUND[hour % 2]) 
            for hour in range(24)
        ]

        # Configure frame
        total_height = self.dims.SCHEDULE_TITLE_HEIGHT + self.dims.CANVAS_HEIGHT
        self.configure(
            width=parent.winfo_width(),
            height=total_height,
            bg=self.colors.BACKGROUND[1]
        )
        
        # Force the frame to keep its size
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        # Setup the UI
        self._setup_ui()
        self._setup_canvas_bindings()
        self.load_blocks(current_date)
        self._schedule_next_time_update()

    def _create_canvases(self):
        # Create schedule title
        schedule_frame = tk.Frame(self, bg=self.colors.BACKGROUND[0])
        schedule_frame.pack(fill="x")
        
        schedule_title = tk.Label(
            schedule_frame,
            text="TIME BLOCKS",
            font=("Arial", 11, "bold"),
            bg=self.colors.BACKGROUND[0],
            fg="#38352A"
        )
        schedule_title.pack(pady=(8, 0), padx=15, anchor="w")
        
        # Create the three canvases
        for name, width in self.dims.CANVAS_WIDTH.items():
            frame = tk.Frame(
                self,
                width=width,
                height=self.dims.CANVAS_HEIGHT,
                bg=self.colors.BACKGROUND[1]
            )
            frame.pack(side="left", fill="both", expand=True)
            
            canvas = tk.Canvas(
                frame,
                width=width,
                height=self.dims.CANVAS_HEIGHT,
                bg=self.colors.BACKGROUND[1],
                highlightthickness=0
            )
            canvas.pack(fill="both", expand=True)
            self.canvases[name] = canvas

    def _setup_ui(self):
        """Set up the main UI components"""
        # Create title frame
        title_frame = tk.Frame(
            self,
            bg=self.colors.BACKGROUND[0],
            height=self.dims.SCHEDULE_TITLE_HEIGHT
        )
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        # Add title
        title = tk.Label(
            title_frame,
            text="TIME BLOCKS",
            font=("Arial", 11, "bold"),
            bg=self.colors.BACKGROUND[0],
            fg="#38352A"
        )
        title.pack(pady=(8, 0), padx=15, anchor="w")
        
        # Create canvas container
        canvas_container = tk.Frame(
            self,
            bg=self.colors.BACKGROUND[1],
            height=self.dims.CANVAS_HEIGHT
        )
        canvas_container.pack(fill="both", expand=True)
        canvas_container.pack_propagate(False)
        
        # Create the three canvases
        for name, width in self.dims.CANVAS_WIDTH.items():
            canvas_frame = tk.Frame(
                canvas_container,
                width=width,
                height=self.dims.CANVAS_HEIGHT,
                bg=self.colors.BACKGROUND[1]
            )
            canvas_frame.pack(side="left", fill="both")
            canvas_frame.pack_propagate(False)
            
            canvas = tk.Canvas(
                canvas_frame,
                width=width,
                height=self.dims.CANVAS_HEIGHT,
                bg=self.colors.BACKGROUND[1],
                highlightthickness=0
            )
            canvas.pack(fill="both", expand=True)
            self.canvases[name] = canvas
        
        # Add button with 3D styling
        add_button = tk.Button(
            canvas_container,
            text="+",
            font=("Arial", 14, "bold"),
            bg=self.colors.ADD_BUTTON_BG,  # Base color remains orange
            fg="white",
            relief="raised",  # Gives 3D effect
            borderwidth=2,
            width=2,
            height=1,
            cursor="hand2"  # Changes cursor on hover
        )
        
        # Configure button appearance
        add_button.configure(
            activebackground="#FF9F1A",  # Slightly lighter orange for hover
            activeforeground="white",
            padx=8,
            pady=4,
            highlightthickness=1,
            highlightbackground="#B67214",  # Darker orange for border
            highlightcolor="#FFB74D"  # Lighter orange for focus
        )
        
        # Add hover effects
        def on_enter(e):
            add_button['relief'] = 'raised'
            add_button['bg'] = '#FF9F1A'  # Lighter shade on hover
            
        def on_leave(e):
            add_button['relief'] = 'raised'
            add_button['bg'] = self.colors.ADD_BUTTON_BG  # Back to original color
            
        def on_press(e):
            add_button['relief'] = 'sunken'  # Pressed effect
            
        def on_release(e):
            add_button['relief'] = 'raised'
            self._show_add_task_dialog()
            
        # Bind hover and click events
        add_button.bind('<Enter>', on_enter)
        add_button.bind('<Leave>', on_leave)
        add_button.bind('<Button-1>', on_press)
        add_button.bind('<ButtonRelease-1>', on_release)
        
        # Remove default command to use our custom binding
        add_button.configure(command='')
        
        # Position the button
        add_button.place(relx=0.95, rely=0.98, anchor="se")
        add_button.place_configure(width=35, height=35)  # Slightly larger size

        # Draw the hour grid
        self._draw_hour_grid()

    def _setup_canvas_bindings(self):
        """Set up the canvas event bindings"""
        task_canvas = self.canvases["task"]
        task_canvas.bind("<B1-Motion>", self._on_drag_motion)
        task_canvas.bind("<ButtonRelease-1>", self._on_drag_release)

    def _draw_hour_grid(self):
        """Optimized hour grid drawing using pre-calculated positions"""
        for canvas in self.canvases.values():
            for y_pos, bg_color in self.HOUR_POSITIONS:
                canvas.create_rectangle(
                    0, y_pos, 
                    canvas.winfo_reqwidth(), 
                    y_pos + self.dims.HOUR_HEIGHT,
                    fill=bg_color, 
                    outline=""
                )

        # Draw hour labels only once
        time_canvas = self.canvases["time"]
        for hour, (y_pos, bg_color) in enumerate(self.HOUR_POSITIONS):
            label = tk.Label(
                time_canvas,
                text=f"{hour:02}:00",
                font=(self.config.FONT_FAMILY, self.config.FONT_SIZES["normal"]),
                bg=bg_color,
                fg="#38352A",
                anchor="w"
            )
            time_canvas.create_window(5, y_pos + 1, window=label, anchor="nw")

    def _show_add_task_dialog(self, task: Optional[Task] = None):
        dialog = Toplevel(self.window)  # Use stored window reference
        dialog.title("Add Task" if task is None else "Edit Task")
        dialog.geometry("300x200")

        task_name = StringVar(value=task.name if task else "")
        start_hour = StringVar(value=f"{int(task.start_time):02}" if task else "00")
        start_minute = StringVar(value=f"{int((task.start_time % 1) * 60):02}" if task else "00")
        end_hour = StringVar(value=f"{int(task.end_time):02}" if task else "00")
        end_minute = StringVar(value=f"{int((task.end_time % 1) * 60):02}" if task else "00")

        self._create_dialog_widgets(dialog, task_name, start_hour, start_minute, end_hour, end_minute, task)

    def _create_dialog_widgets(self, dialog, task_name, start_hour, start_minute, end_hour, end_minute, task=None):
        hours = [f"{i:02}" for i in range(24)]
        minutes = ["00", "15", "30", "45"]

        tk.Label(dialog, text="Task Name").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(dialog, textvariable=task_name).grid(row=0, column=1, padx=5, pady=5)

        for row, (hour_var, minute_var, label) in enumerate([
            (start_hour, start_minute, "Start Time"),
            (end_hour, end_minute, "End Time")
        ], 1):
            tk.Label(dialog, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="w")
            OptionMenu(dialog, hour_var, *hours).grid(row=row, column=1, padx=5, pady=5)
            OptionMenu(dialog, minute_var, *minutes).grid(row=row, column=2, padx=5, pady=5)

        save_button = tk.Button(dialog, text="Save" if task is None else "Update", 
                              command=lambda: self._save_task(dialog, task_name, start_hour, start_minute, end_hour, end_minute, task))
        save_button.grid(row=3, column=1, pady=10)

        if task:
            delete_button = tk.Button(dialog, text="Delete", command=lambda: self._delete_task(dialog, task))
            delete_button.grid(row=3, column=2, pady=10)

    def _save_time_blocks(self):
        """Save all time blocks to storage"""
        # Convert tasks to dictionary format for storage
        tasks_data = [
            {
                'name': task.name,
                'start_time': task.start_time,
                'end_time': task.end_time
            }
            for task in self.tasks
        ]
        
        # Save using data manager
        self.data_manager.save_time_blocks(self.current_date, tasks_data)

    def _save_task(self, dialog, task_name, start_hour, start_minute, end_hour, end_minute, existing_task=None):
        """Save a new task or update an existing one"""
        name = task_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Task name cannot be empty")
            return
            
        # Convert time strings to float values
        start_time = float(start_hour.get()) + float(start_minute.get()) / 60
        end_time = float(end_hour.get()) + float(end_minute.get()) / 60
        
        # Validate times
        if end_time <= start_time:
            messagebox.showerror("Error", "End time must be after start time")
            return
        
        if end_time > 24:
            messagebox.showerror("Error", "End time cannot be after midnight")
            return
            
        # If editing existing task
        if existing_task:
            existing_task.name = name
            existing_task.start_time = start_time
            existing_task.end_time = end_time
            self._update_task_position(existing_task)
        else:
            # Create new task
            new_task = Task(name=name, start_time=start_time, end_time=end_time)
            self.tasks.append(new_task)
            self._draw_task_on_canvas(new_task)
        
        self._save_time_blocks()
        dialog.destroy()

    def _delete_task(self, dialog, task: Task):
        self._remove_task_from_canvas(task)
        self.tasks.remove(task)
        self._save_time_blocks()
        dialog.destroy()

    def _draw_task_on_canvas(self, task: Task):
        start_y = round(task.start_time * self.dims.HOUR_HEIGHT)
        end_y = round(task.end_time * self.dims.HOUR_HEIGHT) - 1
        
        task.box_id = self._create_rounded_rectangle(
            self.canvases["task"],
            30, start_y, 270, end_y,
            self.dims.CORNER_RADIUS,
            self.colors.TASK,
            self.colors.BORDER_DEFAULT,
            self.dims.BORDER_WIDTH
        )
        
        # Calculate center position for text
        text_y = start_y + ((end_y - start_y) / 2)
        
        # Calculate available width for text
        available_width = 220  # 270 - 30 - padding
        
        # Create temporary text to check width
        temp_text = self.canvases["task"].create_text(
            0, 0,  # Position doesn't matter for measurement
            text=task.name,
            font=(self.config.FONT_FAMILY, self.config.FONT_SIZES["normal"], "bold")
        )
        bbox = self.canvases["task"].bbox(temp_text)
        self.canvases["task"].delete(temp_text)
        
        text_width = bbox[2] - bbox[0]
        
        # Truncate text if necessary
        display_text = task.name
        if text_width > available_width:
            display_text = task.name[:int(len(task.name) * (available_width / text_width) - 3)] + "..."
        
        task.text_id = self.canvases["task"].create_text(
            150, text_y,
            text=display_text,
            anchor="center",
            font=(self.config.FONT_FAMILY, self.config.FONT_SIZES["normal"], "bold"),
            fill="#38352A",
            tags=("task_text", str(task.text_id))
        )
        
        # Add tooltip if text was truncated
        if display_text != task.name:
            TooltipManager.setup_tooltip(
                self.canvases["task"],  # Changed from canvas to self.canvases["task"]
                task.name,
                self.config.FONT_FAMILY,
                self.config.FONT_SIZES["normal"],
                self.window,
                is_canvas=True,
                item_ids=[task.box_id, task.text_id]
            )
                
        self._bind_task_events(task)
    
    def _update_task_position(self, task: Task):
        canvas = self.canvases["task"]
        start_y = round(task.start_time * self.dims.HOUR_HEIGHT)
        end_y = round(task.end_time * self.dims.HOUR_HEIGHT) - 1
        
        border_color = self.colors.BORDER_ACTIVE if (self.dragging and task == self.active_task) else self.colors.BORDER_DEFAULT
        fill_color = self.colors.TASK_ACTIVE if (self.dragging and task == self.active_task) else self.colors.TASK
        
        canvas.delete(task.box_id)
        task.box_id = self._create_rounded_rectangle(
            canvas,
            30, start_y, 270, end_y,
            self.dims.CORNER_RADIUS,
            fill_color,
            border_color,
            self.dims.BORDER_WIDTH
        )
        
        canvas.delete(task.text_id)
        
        # Calculate center position for text
        text_y = start_y + ((end_y - start_y) / 2)
        
        # Calculate available width for text
        available_width = 220  # 270 - 30 - padding
        
        # Create temporary text to check width
        temp_text = canvas.create_text(
            0, 0,
            text=task.name,
            font=(self.config.FONT_FAMILY, self.config.FONT_SIZES["normal"], "bold")
        )
        bbox = canvas.bbox(temp_text)
        canvas.delete(temp_text)
        
        text_width = bbox[2] - bbox[0]
        
        # Truncate text if necessary
        display_text = task.name
        if text_width > available_width:
            display_text = task.name[:int(len(task.name) * (available_width / text_width) - 3)] + "..."
        
        task.text_id = canvas.create_text(
            150, text_y,
            text=display_text,
            anchor="center",
            font=(self.config.FONT_FAMILY, self.config.FONT_SIZES["normal"], "bold"),
            fill="#38352A",
            tags=("task_text", str(task.text_id))
        )
        
        # Add tooltip if text was truncated
        if display_text != task.name:
            TooltipManager.setup_tooltip(
                canvas,
                task.name,
                self.config.FONT_FAMILY,
                self.config.FONT_SIZES["normal"],
                self.window,
                is_canvas=True,
                item_ids=[task.box_id, task.text_id]
            )
        
        self._bind_task_events(task)

    def _bind_task_events(self, task):
        """Bind events to task elements"""
        canvas = self.canvases["task"]
        for item_id in [task.box_id, task.text_id]:
            canvas.tag_bind(item_id, "<Enter>", lambda e, t=task: self._on_task_enter(e, t))
            canvas.tag_bind(item_id, "<Leave>", lambda e, t=task: self._on_task_leave(e, t))
            canvas.tag_bind(item_id, "<Motion>", lambda e, t=task: self._on_task_motion(e, t))
            canvas.tag_bind(item_id, "<Button-1>", lambda e, t=task: self._start_drag(e, t))
            canvas.tag_bind(item_id, "<Double-Button-1>", lambda e, t=task: self._show_add_task_dialog(t))

    def _handle_task_interaction(self, event, task, interaction_type, edge=None):
        self.dragging = (interaction_type == 'drag')
        self.resizing = (interaction_type == 'resize')
        self.resize_edge = edge
        self.active_task = task
        self.drag_start_y = event.y
        self.original_start_time = task.start_time
        self.original_end_time = task.end_time
        self.drag_offset = event.y - (task.start_time * self.dims.HOUR_HEIGHT) if interaction_type == 'drag' else 0
        
        self.canvases["task"].itemconfig(task.box_id, fill="#a8c7e6")

    def _on_task_enter(self, event, task: Task):
        """Handle mouse enter event for task"""
        if not (self.dragging or self.resizing):
            self.canvases["task"].itemconfig(
                task.box_id,
                outline="#2b579a"
            )

    def _on_task_leave(self, event, task):
        """Handle mouse leave event for task"""
        if self.dragging or self.resizing:
            return
        
        # Always reset the cursor
        self.window.config(cursor="")
        
        # Reset the border color
        self.canvases["task"].itemconfig(
            task.box_id,
            outline="#bfbfbf"
        )

    def _on_task_motion(self, event, task: Task):
        """Handle mouse motion over task to show resize cursor"""
        if self.resizing or self.dragging:
            return
        
        # Get relative position within task
        task_y = event.y - (task.start_time * self.dims.HOUR_HEIGHT)
        task_height = (task.end_time - task.start_time) * self.dims.HOUR_HEIGHT
        
        canvas = self.canvases["task"]
        mouse_x = canvas.canvasx(event.x)
        mouse_y = canvas.canvasy(event.y)
        bbox = canvas.bbox(task.box_id)
        
        if not bbox:
            self.window.config(cursor="")
            return
            
        x1, y1, x2, y2 = bbox
        if not (x1 <= mouse_x <= x2 and y1 <= mouse_y <= y2):
            self.window.config(cursor="")
            canvas.itemconfig(task.box_id, outline="#bfbfbf")
            return
        
        # Set cursor based on position within task
        if task_y <= 3:
            self.window.config(cursor="sb_v_double_arrow")
        elif task_height - task_y <= 3:
            self.window.config(cursor="sb_v_double_arrow")
        else:
            self.window.config(cursor="")

    def _start_drag(self, event: tk.Event, task: Task) -> None:
        task_y = event.y - (task.start_time * self.dims.HOUR_HEIGHT)
        task_height = (task.end_time - task.start_time) * self.dims.HOUR_HEIGHT
        
        if task_y <= 3:  # Top resize zone
            self._handle_task_interaction(event, task, 'resize', 'top')
        elif task_height - task_y <= 3:  # Bottom resize zone
            self._handle_task_interaction(event, task, 'resize', 'bottom')
        else:
            self._handle_task_interaction(event, task, 'drag')
            self._update_task_position(task)
    
    def _on_drag_motion(self, event):
        if not (self.dragging or self.resizing):
            return

        if self.resizing:
            self._handle_resize_motion(event)
        else:
            self._handle_drag_motion(event)

    def _on_drag_release(self, event):
        """Handle drag release"""
        if not (self.dragging or self.resizing) or not self.active_task:
            return
            
        canvas = self.canvases["task"]
        mouse_x = canvas.canvasx(event.x)
        mouse_y = canvas.canvasy(event.y)
        bbox = canvas.bbox(self.active_task.box_id)
        
        if bbox:
            x1, y1, x2, y2 = bbox
            outline = "#2b579a" if (x1 <= mouse_x <= x2 and y1 <= mouse_y <= y2) else "#bfbfbf"
            canvas.itemconfig(
                self.active_task.box_id,
                fill=self.colors.TASK,
                outline=outline
            )
        
        self.window.config(cursor="")
        
        # Save changes
        tasks_data = [{'name': task.name, 'start_time': task.start_time, 
                      'end_time': task.end_time} for task in self.tasks]
        self.data_manager.save_time_blocks(self.current_date, tasks_data)
        
        # Reset interaction state
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.active_task = None
        self.drag_start_y = 0
        self.original_start_time = 0
        self.original_end_time = 0
        self.drag_offset = 0

    def _handle_resize_motion(self, event):
        if not self.active_task:
            return

        task = self.active_task
        new_y = round((event.y / self.dims.HOUR_HEIGHT) * 4) / 4

        if self.resize_edge == "top":
            if 0 <= new_y < task.end_time - 0.25:  # minimum 15 minutes
                task.start_time = new_y
                self._update_task_position(task)
        elif self.resize_edge == "bottom":
            if task.start_time + 0.25 < new_y <= 24:  # minimum 15 minutes
                task.end_time = new_y
                self._update_task_position(task)

    def _handle_drag_motion(self, event):
        if not self.active_task:
            return

        task = self.active_task
        new_y = event.y - self.drag_offset
        time_delta = round((new_y / self.dims.HOUR_HEIGHT - self.original_start_time) * 4) / 4
        
        new_start_time = self.original_start_time + time_delta
        new_end_time = self.original_end_time + time_delta
        
        if 0 <= new_start_time and new_end_time <= 24:
            task.start_time = new_start_time
            task.end_time = new_end_time
            self._update_task_position(task)

    def _create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius, fill, outline="", width=1):
        """Create a rounded rectangle using a polygon with smooth corners"""
        # Calculate points for the rounded corners
        points = [
            x1 + radius, y1,  # Top edge
            x2 - radius, y1,
            x2, y1,  # Top right corner
            x2, y1 + radius,
            x2, y2 - radius,  # Right edge
            x2, y2,  # Bottom right corner
            x2 - radius, y2,
            x1 + radius, y2,  # Bottom edge
            x1, y2,  # Bottom left corner
            x1, y2 - radius,
            x1, y1 + radius,  # Left edge
            x1, y1  # Top left corner
        ]
        
        return canvas.create_polygon(
            points,
            smooth=True,
            fill=fill,
            outline=outline,
            width=width
        )  

    def load_blocks(self, date):
        """Load time blocks for a specific date"""
        self.current_date = date
        self.tasks.clear()
        for canvas in self.canvases.values():
            canvas.delete("all")
        self._draw_hour_grid()
        
        blocks = self.data_manager.load_time_blocks(date)
        for block_data in blocks:
            task = Task(**block_data)
            self.tasks.append(task)
            self._draw_task_on_canvas(task)
        
        if self.current_date == datetime.now().date():
            self._schedule_next_time_update()

    def _schedule_next_time_update(self):
        """Schedule the next time marker update"""
        # Cancel any existing scheduled update
        if self._scheduled_update:
            self.window.after_cancel(self._scheduled_update)
            self._scheduled_update = None

        if self.current_date == datetime.now().date():
            now = datetime.now()
            next_update = now + timedelta(minutes=(15 - now.minute % 15))
            next_update = next_update.replace(second=0, microsecond=0)
            delay = int((next_update - now).total_seconds() * 1000)
            
            self._update_time_marker()
            self._scheduled_update = self.window.after(delay, self._schedule_next_time_update)
        else:
            self.canvases["now"].delete("triangle")

    def _update_time_marker(self):
        """Update the current time marker"""
        if self.current_date != datetime.now().date():
            self.canvases["now"].delete("triangle")
            return

        now = datetime.now()
        current_y = (now.hour + now.minute / 60) * self.dims.HOUR_HEIGHT - self.dims.HOUR_MARKER_OFFSET

        self.canvases["now"].delete("triangle")
        self.canvases["now"].create_text(
            25, current_y,
            text="▶",
            fill="orange",
            font=("Arial", 30),
            anchor="n",
            tags="triangle"
        )
    
    def _remove_task_from_canvas(self, task: Task):
        """Remove task items from canvas"""
        for item_id in [task.box_id, task.text_id]:
            if item_id:
                self.canvases["task"].delete(item_id)