import tkinter as tk

def highlight_cells(locations, start_x, start_y, cell_width, cell_height, root, color, thickness=2):
    """
    Highlight the cells on the screen.
    
    Args:
        locations (list of tuple): List of tuples representing the coordinates of the cells.
        start_x (int): The starting x-coordinate of the grid.
        start_y (int): The starting y-coordinate of the grid.
        cell_width (int): The width of each cell in the grid.
        cell_height (int): The height of each cell in the grid.
        root (tk.Tk): The root Tkinter window.
        color (str): The color to highlight the cells.
        thickness (int): The thickness of the highlight box lines.
    """
    # Check if overlay already exists, if not create one
    if not hasattr(root, 'overlay'):
        root.overlay = tk.Toplevel(root)
        root.overlay.attributes("-transparentcolor", "magenta")
        root.overlay.attributes("-topmost", True)
        root.overlay.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
        root.overlay.overrideredirect(True)
        root.canvas = tk.Canvas(root.overlay, width=root.winfo_screenwidth(), height=root.winfo_screenheight(), bg='magenta', highlightthickness=0)
        root.canvas.pack()
    else:
        # Clear the existing boxes of the same color
        items = root.canvas.find_withtag(color)
        for item in items:
            root.canvas.delete(item)

    for loc in locations:
        row, col = loc
        screen_x = start_x + col * cell_width + 1
        screen_y = start_y + row * cell_height + 1
        root.canvas.create_rectangle(screen_x, screen_y, screen_x + cell_width - 2, screen_y + cell_height - 2, outline=color, width=thickness, tags=color)
