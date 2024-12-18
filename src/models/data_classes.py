from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class Task:
    name: str
    start_time: float
    end_time: float
    box_id: Optional[int] = None
    text_id: Optional[int] = None

@dataclass
class TopTask:
    text: str
    completed: bool = False

@dataclass
class InteractionState:
    _top_tasks: List[TopTask] = field(default_factory=list)
    dragging: bool = False
    resizing: bool = False
    resize_edge: Optional[str] = None
    active_task: Optional[Task] = None
    drag_start_y: float = 0
    original_start_time: float = 0
    original_end_time: float = 0
    drag_offset: float = 0

    @property
    def top_tasks(self) -> List[TopTask]:
        return self._top_tasks

    @top_tasks.setter
    def top_tasks(self, value: List[TopTask]):
        self._top_tasks = value.copy() if value else []

    def reset_interaction_only(self):
        """Reset only interaction-related state"""
        self.dragging = False
        self.resizing = False
        self.resize_edge = None
        self.active_task = None
        self.drag_start_y = 0
        self.original_start_time = 0
        self.original_end_time = 0
        self.drag_offset = 0

    def update(self, **kwargs):
        """Update only specific fields while preserving others"""
        # Make a copy of top_tasks to preserve it
        preserved_tasks = self.top_tasks.copy()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        # Restore top_tasks if it wasn't explicitly updated
        if 'top_tasks' not in kwargs:
            self.top_tasks = preserved_tasks
        return self

@dataclass(frozen=True)
class Colors:
    # Background colors
    BACKGROUND: List[str] = field(default_factory=lambda: ["#F7F5EE", "#EBE9DC"])
    HEADER: str = "#EBE9DC"
    
    # Task colors
    TASK: str = "#D4CFBE"
    TASK_ACTIVE: str = "#a8c7e6"
    TASK_TEXT: str = "#38352A"
    
    # Border colors
    BORDER_DEFAULT: str = "#949185"
    BORDER_ACTIVE: str = "#2b579a"
    
    # Priority task colors
    PRIORITY_BOX_BG: str ="#DBD5C2"
    PRIORITY_NUMBER_BG: str = "#E8931A"  # Orange background for priority numbers
    PRIORITY_NUMBER_TEXT: str = "#EBE9DC"
    PRIORITY_TASK_BG: str = "#DBD5C2"
    PRIORITY_TASK_TEXT: str = "#38352A"
    PRIORITY_TASK_COMPLETED: str = "#2E8B57"  # Sea Green for completed tasks

    # Add button colors
    ADD_BUTTON_BG: str = "#E8931A"  # Same as priority numbers for consistency
    ADD_BUTTON_TEXT: str = "white"
    
    # Time marker color
    TIME_MARKER: str = "#E8931A"
    
    # Handle color (kept for compatibility)
    HANDLE: str = "#6fa8dc"


@dataclass(frozen=True)
class Dimensions:
    # Base units
    HOUR_HEIGHT: int = 32  # Height per hour in the time grid
    HOUR_MARKER_OFFSET: int = 22  # Offset for the current time marker
    
    # Fixed section heights
    NAV_HEIGHT: int = 40  # Navigation bar height
    SCHEDULE_TITLE_HEIGHT: int = 30  # "TIME BLOCKS" title height
    
    # Top tasks section components
    TOP_TASK_TITLE_HEIGHT: int = 28  # Title + padding
    TOP_TASK_FRAME_HEIGHT: int = 41  # Single task frame height
    TOP_TASK_SPACING: int = 2  # Spacing between task frames
    TOP_TASK_BOTTOM_PADDING: int = 10  # Bottom padding
    
    # Other measurements
    CORNER_RADIUS: int = 8
    BORDER_WIDTH: int = 1
    
    # Canvas widths
    CANVAS_WIDTH: Dict[str, int] = field(default_factory=lambda: {
        "now": 50,
        "time": 50,
        "task": 300
    })
    
    @property
    def TOP_TASKS_HEIGHT(self) -> int:
        """Total height of the top tasks section"""
        return (self.TOP_TASK_TITLE_HEIGHT +  # Title area
                (self.TOP_TASK_FRAME_HEIGHT * 3) +  # Three task frames
                (self.TOP_TASK_SPACING * 2) +  # Spacing between tasks
                self.TOP_TASK_BOTTOM_PADDING)  # Bottom padding
    
    @property
    def CANVAS_HEIGHT(self) -> int:
        """Height of the time grid canvas (24 hours)"""
        return 24 * self.HOUR_HEIGHT  # 24 hours * height per hour
    
    @property
    def TIME_BLOCKS_HEIGHT(self) -> int:
        """Total height of the time blocks section including title"""
        return self.SCHEDULE_TITLE_HEIGHT + self.CANVAS_HEIGHT
    
    @property
    def TOTAL_HEIGHT(self) -> int:
        """Total window height"""
        return (self.NAV_HEIGHT +  # Date navigation bar
                self.TOP_TASKS_HEIGHT +  # Priority tasks section
                self.TIME_BLOCKS_HEIGHT)  # Time blocks section (including title)

@dataclass(frozen=True)
class UIConfig:
    SAVE_FILE: str = "tasks.json"
    FONT_FAMILY: str = "Arial"
    FONT_SIZES: Dict[str, int] = field(default_factory=lambda: {
        "normal": 10,
        "bold": 12 
    })

@dataclass(frozen=True)
class AppConstants:
    DATE_FORMAT: str = "%Y-%m-%d"
    MIN_TASK_DURATION: float = 0.25  # 15 minutes