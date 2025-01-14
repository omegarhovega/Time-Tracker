import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar
from src.models.data_classes import Colors, UIConfig, Dimensions 

class DateNavigationBar(tk.Frame):
    def __init__(self, parent, initial_date, on_date_change):
        super().__init__(parent)
        
        # Store reference to main window
        self.window = parent.winfo_toplevel()
        
        # Force the frame to keep its size
        self.dims = Dimensions()
        self.pack_propagate(False)
        self.grid_propagate(False)
        # Set fixed size
        self.configure(width=parent.winfo_width(), height=self.dims.NAV_HEIGHT)
        
        self.colors = Colors()
        self.config = UIConfig()
        self.current_date = initial_date
        self.on_date_change = on_date_change
        
        # Setup keyboard shortcuts
        self._setup_shortcuts()
        
        self._setup_ui()

    def _setup_shortcuts(self):
        """Setup keyboard shortcuts for date navigation"""
        # Bind arrow keys for date navigation
        self.window.bind('<Left>', lambda e: self._change_date(-1))
        self.window.bind('<Right>', lambda e: self._change_date(1))

    def _change_date(self, days: int):
        """Change the current date by the specified number of days"""
        self.current_date += timedelta(days=days)
        self.date_label.config(text=self.current_date.strftime("%A, %d %B %Y"))
        self.on_date_change(self.current_date)
        return "break"  # Prevents the event from propagating
    
    def _setup_ui(self):
        """Set up the navigation controls with calendar and today button"""
        # Set frame background
        self.configure(bg=self.colors.HEADER)
        
        # Common button style setup
        button_style = {
            'font': (self.config.FONT_FAMILY, 11, "bold"),
            'bg': "#DBD5C2",
            'relief': 'raised',
            'borderwidth': 2,
            'cursor': 'hand2',
            'activebackground': '#E8E4D6',  # Lighter shade for hover
            'activeforeground': '#38352A'    # Darker text on hover
        }
        
        # Navigation button style (specifically for arrows)
        nav_button_style = {
            **button_style,
            'width': 1,      
            'padx': 2,       
            'pady': 4
        }
        
        # Today button style
        today_button_style = {
            **button_style,
            'padx': 8,
            'pady': 4
        }
        
        # Previous day button
        self.prev_button = tk.Button(
            self,
            text="◀",
            command=lambda: self._change_date(-1),
            **nav_button_style
        )
        self.prev_button.pack(side="left", padx=5, pady=5)
        
        # Date label (clickable for calendar)
        self.date_label = tk.Label(
            self,
            text=self.current_date.strftime("%A, %d %B %Y"),
            font=(self.config.FONT_FAMILY, 12, "bold"),
            bg=self.colors.HEADER,
            fg=self.colors.PRIORITY_TASK_TEXT,
            cursor="hand2"
        )
        self.date_label.pack(side="left", expand=True)
        self.date_label.bind("<Button-1>", self._show_calendar)
        
        # Today button
        self.today_button = tk.Button(
            self,
            text="Today",
            command=self._go_to_today,
            **today_button_style
        )
        self.today_button.pack(side="right", padx=5, pady=5)
        
        # Next day button
        self.next_button = tk.Button(
            self,
            text="▶",
            command=lambda: self._change_date(1),
            **nav_button_style
        )
        self.next_button.pack(side="right", padx=5, pady=5)
        
        # Add hover effects to all buttons
        for button in [self.prev_button, self.today_button, self.next_button]:
            self._add_button_hover_effects(button)

    def _add_button_hover_effects(self, button):
        """Add hover and click effects to a button"""
        def on_enter(e):
            button['relief'] = 'raised'
            button['bg'] = '#E8E4D6'  # Lighter shade on hover
            
        def on_leave(e):
            button['relief'] = 'raised'
            button['bg'] = '#DBD5C2'  # Back to original color
            
        def on_press(e):
            button['relief'] = 'sunken'  # Pressed effect
            
        def on_release(e):
            button['relief'] = 'raised'
            button['bg'] = '#E8E4D6'  # Keep hover color if still hovering
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        button.bind('<Button-1>', on_press)
        button.bind('<ButtonRelease-1>', on_release)

    def _change_date(self, days: int):
        """Change the current date by the specified number of days"""
        self.current_date += timedelta(days=days)
        self.date_label.config(text=self.current_date.strftime("%A, %d %B %Y"))
        self.on_date_change(self.current_date)

    def _go_to_today(self):
        """Jump to today's date"""
        self.current_date = datetime.now().date()
        self.date_label.config(text=self.current_date.strftime("%A, %d %B %Y"))
        self.on_date_change(self.current_date)

    def _show_calendar(self, event=None):
        """Show the calendar dialog"""
        CalendarDialog(self, self.current_date, self._set_date)
    
    def _set_date(self, new_date):
        """Set the current date and update the view"""
        self.current_date = new_date
        self.date_label.config(text=self.current_date.strftime("%A, %d %B %Y"))
        self.on_date_change(self.current_date)

class CalendarDialog:
    def __init__(self, parent, current_date, callback):
        self.colors = Colors()
        self.top = tk.Toplevel(parent)
        self.top.title("Select Date")
        self.callback = callback
        self.current_date = current_date
        
        # Set up variables
        self.year = current_date.year
        self.month = current_date.month
        
        self._setup_ui()
        
        # Center the dialog
        self.top.transient(parent)
        self.top.grab_set()
        parent.wait_window(self.top)
    
    def _setup_ui(self):
        # Create and configure styles
        style = ttk.Style()
        style.configure(
            'Calendar.TLabel',
            foreground=self.colors.PRIORITY_TASK_TEXT,
            font=("Arial", 9, "bold")
        )
        style.configure(
            'CalendarHeader.TLabel',
            foreground=self.colors.PRIORITY_TASK_TEXT,
            font=("Arial", 10, "bold")
        )
        
        # Month and Year Navigation
        nav_frame = ttk.Frame(self.top)
        nav_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(nav_frame, text="◀", width=3,
                command=self._prev_month).pack(side="left")
        self.month_year_label = ttk.Label(
            nav_frame, 
            text="",
            style='CalendarHeader.TLabel'
        )
        self.month_year_label.pack(side="left", expand=True, padx=10)
        ttk.Button(nav_frame, text="▶", width=3,
                command=self._next_month).pack(side="right")
        
        # Calendar Frame
        self.cal_frame = ttk.Frame(self.top)
        self.cal_frame.pack(padx=5, pady=5)
        
        # Weekday headers
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(weekdays):
            ttk.Label(
                self.cal_frame, 
                text=day,
                style='Calendar.TLabel'
            ).grid(row=0, column=i, padx=2, pady=2)
        
        self._draw_calendar()
    
    def _draw_calendar(self):
        # Update month/year label
        self.month_year_label.config(
            text=f"{calendar.month_name[self.month]} {self.year}")
        
        # Clear existing calendar buttons
        for widget in self.cal_frame.grid_slaves():
            if widget.grid_info()["row"] > 0:  # Don't remove headers
                widget.destroy()
        
        # Get calendar for current month
        cal = calendar.monthcalendar(self.year, self.month)
        
        # Create date buttons
        today = datetime.now().date()
        for week_num, week in enumerate(cal, 1):
            for day_num, day in enumerate(week):
                if day != 0:
                    btn = ttk.Button(
                        self.cal_frame,
                        text=str(day),
                        width=4,
                        command=lambda d=day: self._select_date(d)
                    )
                    btn.grid(row=week_num, column=day_num, padx=1, pady=1)
                    
                    # Highlight current date
                    date = datetime(self.year, self.month, day).date()
                    if date == today:
                        btn.state(['pressed'])  # Visual indication for today
                    elif date == self.current_date:
                        btn.state(['alternate'])  # Visual indication for selected date
    
    def _prev_month(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self._draw_calendar()
    
    def _next_month(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self._draw_calendar()
    
    def _select_date(self, day):
        selected_date = datetime(self.year, self.month, day).date()
        self.callback(selected_date)
        self.top.destroy()