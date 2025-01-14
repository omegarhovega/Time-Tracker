import tkinter as tk
from tkinter import Toplevel
from src.models.data_classes import TopTask, Colors, Dimensions
from src.utils.tooltip import TooltipManager
from src.data_manager import DataManager

class TopTasksSection(tk.Frame):
    def __init__(self, parent, current_date):
        super().__init__(parent)

        # Store reference to main window and ensure it's the root window
        self.window = parent.winfo_toplevel()
        
        # Rest of your existing initialization code...
        self.dims = Dimensions()
        self.pack_propagate(False)
        self.grid_propagate(False)
        self.configure(width=parent.winfo_width(), height=self.dims.TOP_TASKS_HEIGHT)
        
        self.colors = Colors() 
        self.configure(bg=self.colors.PRIORITY_BOX_BG)
        self.current_date = current_date
        self.data_manager = DataManager()
        
        self.checkboxes = {}
        self.task_frames = []
        self.state = []
        
        self.tasks_container = tk.Frame(
            self,
            bg=self.colors.PRIORITY_BOX_BG
        )
        
        # Setup keyboard shortcuts with explicit binding to root window
        self.after(100, self._setup_shortcuts)  # Delay to ensure window is fully initialized
        
        self._setup_ui()
        self.load_tasks(current_date)

    def _setup_ui(self):
        """Set up the main UI components"""
        title = tk.Label(
            self,
            text="TODAY'S PRIORITIES",
            font=("Arial", 11, "bold"),
            bg=self.colors.PRIORITY_BOX_BG,
            fg=self.colors.PRIORITY_TASK_TEXT
        )
        title.pack(pady=(8, 0), padx=15, anchor="w")
        
        # Pack the tasks container
        self.tasks_container.pack(fill="both", expand=True, padx=5)

    def load_tasks(self, date):
        """Load priority tasks for a specific date"""
        self.current_date = date
        
        # Clear existing task frames
        for frame in self.task_frames:
            frame.destroy()
        self.task_frames = []
        self.checkboxes = {}
        
        # Load tasks from data manager
        tasks = self.data_manager.load_top_tasks(date)
        if not tasks:
            # Initialize with default empty tasks
            tasks = [
                {'text': 'Click to add priority task 1', 'completed': False},
                {'text': 'Click to add priority task 2', 'completed': False},
                {'text': 'Click to add priority task 3', 'completed': False}
            ]
            self.data_manager.save_top_tasks(date, tasks)
        
        # Create task frames
        self.state = [TopTask(**task) for task in tasks]
        for i, task in enumerate(self.state):
            frame = self._create_task_frame(i, task)
            if frame:
                frame.pack(in_=self.tasks_container, fill="x", pady=1)
                self.task_frames.append(frame)

    def _create_task_frame(self, index, task):
        """Create a frame for a single task"""
        if not task:
            return None
            
        # Main container frame
        frame = tk.Frame(self.tasks_container, bg=self.colors.PRIORITY_BOX_BG, padx=15, pady=2)
        
        # Task number tag frame
        tag_frame = tk.Frame(frame, bg=self.colors.PRIORITY_NUMBER_BG, width=30, height=25)
        tag_frame.pack_propagate(False)
        tag_frame.pack(side="left", padx=(0, 15))
        
        # Task number label
        tk.Label(
            tag_frame,
            text=f"0{index + 1}",
            font=("Arial", 10, "bold"),
            bg=self.colors.PRIORITY_NUMBER_BG,
            fg=self.colors.PRIORITY_NUMBER_TEXT
        ).pack(expand=True)
        
        # Task content frame with full width
        content_frame = tk.Frame(frame, bg=self.colors.PRIORITY_TASK_BG)
        content_frame.pack(side="left", fill="both", expand=True, pady=6)
        
        # Create checkbox
        checkbox_var = tk.BooleanVar(value=task.completed)
        self.checkboxes[index] = checkbox_var
        
        checkbox_frame = tk.Frame(content_frame, bg=self.colors.PRIORITY_TASK_BG)
        checkbox_frame.pack(side="left", padx=15)
        
        cb = tk.Checkbutton(
            checkbox_frame,
            bg=self.colors.PRIORITY_TASK_BG,
            variable=checkbox_var,
            command=lambda i=index: self._toggle_task(i)
        )
        cb.pack()
        
        if task.completed:
            cb.select()
        else:
            cb.deselect()

        # Task text label
        label = self._create_task_label(content_frame, task, index)
        label.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        return frame

    def _create_task_label(self, parent, task, index):
        """Create the label for a task"""
        truncated_text = self._truncate_text(task.text)
        
        label = tk.Label(
            parent,
            text=truncated_text,
            font=("Arial", 11, "overstrike" if task.completed else "normal"),
            bg=self.colors.PRIORITY_TASK_BG,
            fg=self.colors.PRIORITY_TASK_COMPLETED if task.completed else self.colors.PRIORITY_TASK_TEXT,
            cursor="hand2",
            anchor="w",
            width=29
        )
        
        # Bind click event for editing
        label.bind("<Button-1>", lambda e, i=index: self._edit_task(i))
        
        # Set up tooltip if needed
        self._setup_tooltip(label, task.text)
        
        return label

    def _setup_tooltip(self, label, full_text):
        """Set up tooltip for a label if text is too long"""
        if hasattr(label, 'tooltip') and label.tooltip is not None:
            try:
                label.tooltip.destroy()
                label.tooltip = None
            except tk.TclError:
                pass
        
        label.unbind('<Enter>')
        label.unbind('<Leave>')
        
        if len(full_text) > 29:
            TooltipManager.setup_tooltip(
                label,
                full_text,
                "Arial",
                11
            )

    def _truncate_text(self, text, max_length=29):
        """Truncate text if it's too long"""
        if len(text) > max_length:
            return text[:max_length-3] + "..."
        return text
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts for editing tasks"""
        # Bind to both the root window and the frame itself
        root = self.winfo_toplevel()
        
        # Define the bindings
        shortcuts = {
            '<Control-Key-1>': lambda e: self._handle_task_shortcut(0),
            '<Control-Key-2>': lambda e: self._handle_task_shortcut(1),
            '<Control-Key-3>': lambda e: self._handle_task_shortcut(2)
        }
        
        # Apply bindings to root window
        for shortcut, handler in shortcuts.items():
            root.bind(shortcut, handler)
            self.window.bind(shortcut, handler)

    def _handle_task_shortcut(self, index):
        """Handle keyboard shortcut for editing a specific task"""
        if index < len(self.state):
            self._edit_task(index)
        return "break"

    def _toggle_task(self, index):
        """Handle task completion toggle"""
        if index >= len(self.state):
            return
            
        task = self.state[index]
        checkbox_var = self.checkboxes.get(index)
        if checkbox_var is None:
            return
        
        # Update completion status
        task.completed = checkbox_var.get()
        
        # Update UI
        content_frame = self.task_frames[index].winfo_children()[1]
        label = content_frame.winfo_children()[1]
        
        label.config(
            fg=self.colors.PRIORITY_TASK_COMPLETED if task.completed else self.colors.PRIORITY_TASK_TEXT,
            font=("Arial", 11, "overstrike" if task.completed else "normal")
        )
        
        # Save changes
        self._save_tasks()

    def _edit_task(self, index):
        """Show dialog to edit task"""
        if index >= len(self.state):
            return
            
        dialog = Toplevel(self)
        dialog.title(f"Edit Priority {index + 1}")
        dialog.geometry("300x100")
        
        dialog.transient(self)
        dialog.grab_set()
        
        entry_var = tk.StringVar(value=self.state[index].text)
        entry = tk.Entry(dialog, textvariable=entry_var, width=40)
        entry.pack(padx=10, pady=10)
        entry.select_range(0, tk.END)
        entry.focus()
        
        def save():
            self._save_task_edit(index, entry_var.get().strip(), dialog)
        
        def handle_escape(event):
            dialog.destroy()
        
        save_btn = tk.Button(dialog, text="Save", command=save)
        save_btn.pack(pady=5)
        
        # Bind Return and Escape keys
        entry.bind("<Return>", lambda e: save())
        dialog.bind("<Escape>", handle_escape)
        entry.bind("<Escape>", handle_escape)

    def _save_task_edit(self, index, new_text, dialog):
        """Save edited task text"""
        if not new_text:
            return
        
        self.state[index].text = new_text
        content_frame = self.task_frames[index].winfo_children()[1]
        label = content_frame.winfo_children()[1]
        
        # Update label with new text
        truncated_text = self._truncate_text(new_text)
        label.config(text=truncated_text)
        
        # Update tooltip if needed
        self._setup_tooltip(label, new_text)
        
        # Save changes
        self._save_tasks()
        dialog.destroy()

    def _save_tasks(self):
        """Save all tasks to storage"""
        tasks_data = [{'text': task.text, 'completed': task.completed} 
                     for task in self.state]
        self.data_manager.save_top_tasks(self.current_date, tasks_data)