import tkinter as tk

class TooltipManager:
    @staticmethod
    def setup_tooltip(label_or_canvas, full_text, font_family="Arial", font_size=11, parent=None, is_canvas=False, x=None, y=None, item_ids=None):
        """
        Set up tooltip for either a label or canvas text
        
        Parameters:
        - label_or_canvas: tk.Label or tk.Canvas widget
        - full_text: Text to show in tooltip
        - font_family: Font family to use
        - font_size: Font size to use
        - parent: Parent window (needed for canvas tooltips)
        - is_canvas: Whether this is for a canvas text
        - item_ids: List of canvas item IDs that should trigger the tooltip (for canvas only)
        """
        widget = label_or_canvas
        
        # First clean up any existing tooltip
        if hasattr(widget, 'tooltip') and widget.tooltip is not None:
            try:
                widget.tooltip.destroy()
                widget.tooltip = None
            except tk.TclError:
                pass
        
        # Remove existing bindings
        if is_canvas and item_ids:
            for item_id in item_ids:
                for bind_tag in widget.tag_bind(item_id):
                    if str(bind_tag).startswith('tooltip'):
                        widget.tag_unbind(item_id, bind_tag)
        else:
            widget.unbind('<Enter>')
            widget.unbind('<Leave>')
        
        widget.tooltip = None
        
        def create_tooltip(event):
            destroy_tooltip()

            tooltip = tk.Toplevel(parent if is_canvas else widget)
            tooltip.wm_overrideredirect(True)
            tooltip.attributes('-transparentcolor', '#F0F0F0')
            
            # Calculate text dimensions
            temp_label = tk.Label(tooltip, text=full_text, font=(font_family, font_size))
            text_width = temp_label.winfo_reqwidth()
            text_height = temp_label.winfo_reqheight()
            temp_label.destroy()
            
            canvas_width = text_width + 40
            canvas_height = text_height + 16
            
            canvas = tk.Canvas(
                tooltip,
                width=canvas_width,
                height=canvas_height,
                bg='#F0F0F0',
                highlightthickness=0
            )
            canvas.pack()

            # Define coordinates for rounded rectangle
            radius = 8
            x1, y1 = 1, 1
            x2 = canvas_width - 1
            y2 = canvas_height - 1
            
            # Create rounded rectangle
            canvas.create_polygon(
                x1+radius, y1,
                x2-radius, y1,
                x2, y1,
                x2, y1+radius,
                x2, y2-radius,
                x2, y2,
                x2-radius, y2,
                x1+radius, y2,
                x1, y2,
                x1, y2-radius,
                x1, y1+radius,
                x1, y1,
                smooth=True,
                fill="white",
                outline="#38352A"
            )
            
            canvas.create_text(
                canvas_width/2,
                canvas_height/2,
                text=full_text,
                font=(font_family, font_size),
                fill="#38352A",
                anchor="center",
                width=canvas_width-20
            )

            widget.tooltip = tooltip

            # Position tooltip based on widget type
            if is_canvas and item_ids:
                # For time block tasks
                text_bbox = widget.bbox(item_ids[1])  # Use text item ID for positioning
                if not text_bbox:
                    return
                
                # Calculate position relative to the text
                tooltip_x = widget.winfo_rootx() + text_bbox[0] + (text_bbox[2] - text_bbox[0]) // 2 - canvas_width // 2
                tooltip_y = widget.winfo_rooty() + text_bbox[3] + 5
            else:
                # For top tasks (preserve original behavior)
                tooltip_x = widget.winfo_rootx()
                tooltip_y = widget.winfo_rooty() + widget.winfo_height() + 5
            
            # Ensure tooltip stays within screen bounds
            screen_width = tooltip.winfo_screenwidth()
            if tooltip_x + canvas_width > screen_width:
                tooltip_x = screen_width - canvas_width - 10
            if tooltip_x < 0:
                tooltip_x = 10
            
            tooltip.wm_geometry(f"+{tooltip_x}+{tooltip_y}")
            tooltip.wm_attributes("-topmost", True)

        def destroy_tooltip():
            if hasattr(widget, 'tooltip') and widget.tooltip is not None:
                try:
                    widget.tooltip.destroy()
                    widget.tooltip = None
                except tk.TclError:
                    pass

        # Add new bindings
        if is_canvas and item_ids:
            # For time block tasks
            for item_id in item_ids:
                widget.tag_bind(item_id, '<Enter>', create_tooltip, add='+')
                widget.tag_bind(item_id, '<Leave>', lambda e: destroy_tooltip(), add='+')
        else:
            # For top tasks (preserve original behavior)
            if len(full_text) > 29:  # Only add bindings for labels if text is too long
                widget.bind('<Enter>', create_tooltip, add='+')
                widget.bind('<Leave>', lambda e: destroy_tooltip(), add='+')