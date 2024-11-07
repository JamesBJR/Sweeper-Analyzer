import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab, Image, ImageTk
import pyautogui
import numpy as np
import cv2
import json
import time
import threading
# from screen_capture.capture import capture_screen
# from image_processing.process_image import process_image
from board_analysis.analyze_board import analyze_board
from bomb_calculation.calculate_bombs import calculate_bombs

def capture_screen(region):
    screenshot = pyautogui.screenshot(region=region)
    return screenshot

def process_image(image):
    # Convert PIL Image to NumPy array if necessary
    if isinstance(image, Image.Image):
        image = np.array(image)
    
    # Add more image processing steps here
    return image

def start_gui():
    root = tk.Tk()
    root.title("Sweeper Analyzer")

    # Add GUI components here
    select_area_button = tk.Button(root, text="Select Area", command=lambda: select_area(root))
    select_area_button.pack(pady=10)

    analyze_button = tk.Button(root, text="Analyze", command=lambda: analyze_area(root))
    analyze_button.pack(pady=10)

    generate_template_button = tk.Button(root, text="Generate Templates", command=lambda: open_template_window(root))
    generate_template_button.pack(pady=10)

    get_board_size_button = tk.Button(root, text="Get Board Size", command=lambda: get_board_size(root))
    get_board_size_button.pack(pady=10)

    clear_overlays_button = tk.Button(root, text="Clear Overlays", command=lambda: clear_overlays(root))
    clear_overlays_button.pack(pady=10)

    # Create input boxes for rows, columns, and cell size
    global rows_entry, cols_entry, cell_size_entry
    rows_label = tk.Label(root, text="Rows:")
    rows_label.pack(pady=5)
    rows_entry = tk.Entry(root)
    rows_entry.pack(pady=5)

    cols_label = tk.Label(root, text="Columns:")
    cols_label.pack(pady=5)
    cols_entry = tk.Entry(root)
    cols_entry.pack(pady=5)

    cell_size_label = tk.Label(root, text="Cell Size:")
    cell_size_label.pack(pady=5)
    cell_size_entry = tk.Entry(root)
    cell_size_entry.pack(pady=5)

    # Load the last entered rows, columns, and cell size from the JSON file
    try:
        with open("grid_settings.json", "r") as file:
            data = json.load(file)
            rows_entry.insert(0, str(data.get("rows", "")))
            cols_entry.insert(0, str(data.get("cols", "")))
            cell_size_entry.insert(0, str(data.get("cell_size", "")))
    except FileNotFoundError:
        pass

    # Load the last entered coordinates from the JSON file
    try:
        with open("sweeper_coordinates.json", "r") as file:
            data = json.load(file)
            rows_entry.insert(0, str(data.get("rows", "")))
            cols_entry.insert(0, str(data.get("cols", "")))
            cell_size_entry.insert(0, str(data.get("cell_size", "")))
    except FileNotFoundError:
        pass

    # Create a label to display the analyzed image
    global image_label
    image_label = tk.Label(root)
    image_label.pack(pady=10)

    # Add a checkbox to keep the window on top
    keep_on_top_var = tk.BooleanVar(value=True)
    keep_on_top_checkbox = tk.Checkbutton(root, text="Keep on Top", variable=keep_on_top_var, command=lambda: toggle_on_top(root, keep_on_top_var))
    keep_on_top_checkbox.pack(pady=10)

    # Add a checkbox for Debug
    global debug_var
    debug_var = tk.BooleanVar(value=False)
    debug_checkbox = tk.Checkbutton(root, text="Debug", variable=debug_var)
    debug_checkbox.pack(pady=10)

    # Add a checkbox for auto-analyze
    global auto_analyze_var
    auto_analyze_var = tk.BooleanVar(value=False)
    auto_analyze_checkbox = tk.Checkbutton(root, text="Auto Analyze", variable=auto_analyze_var, command=lambda: auto_analyze(root))
    auto_analyze_checkbox.pack(pady=10)

    # Set the window to be on top by default
    root.wm_attributes("-topmost", keep_on_top_var.get())

    root.mainloop()

def toggle_on_top(root, keep_on_top_var):
    root.wm_attributes("-topmost", keep_on_top_var.get())

def select_area(root):
    # Hide the window to take a screenshot of full screen
    root.withdraw()
    time.sleep(0.5)  # Small delay to make sure the window is hidden

    # Take screenshot of the full screen
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)

    # Create a new tkinter window to select the area
    selection_window = tk.Toplevel(root)
    selection_window.attributes("-fullscreen", True)
    selection_window.attributes("-alpha", 0.3)
    selection_window.configure(bg='black')

    selection_canvas = tk.Canvas(selection_window, cursor="cross", bg='black')
    selection_canvas.pack(fill="both", expand=True)

    # Create a small zoom window
    zoom_window = tk.Toplevel(selection_window)
    zoom_window.title("Zoom View")
    zoom_window.geometry("200x200")  # Fixed size for zoom window
    zoom_label = tk.Label(zoom_window)
    zoom_label.pack()

    rect = None
    start_x, start_y = None, None

    def on_mouse_down(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        rect = selection_canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red', width=2)

    def on_mouse_move(event):
        if rect is not None:
            selection_canvas.coords(rect, start_x, start_y, event.x, event.y)

        # Update zoom window
        x, y = event.x, event.y
        zoom_size = 40  # Size of the area to zoom in on
        zoom_factor = 5  # Zoom factor

        # Calculate bounding box for zoom area
        left = max(0, x - zoom_size // 2)
        top = max(0, y - zoom_size // 2)
        right = min(screenshot.shape[1], x + zoom_size // 2)
        bottom = min(screenshot.shape[0], y + zoom_size // 2)

        # Crop and resize the zoom area
        zoom_area = screenshot[top:bottom, left:right]
        zoom_area = cv2.resize(zoom_area, (zoom_size * zoom_factor, zoom_size * zoom_factor), interpolation=cv2.INTER_LINEAR)

        # Draw a box around the center pixel
        zoom_area = np.array(zoom_area)
        center_x = zoom_area.shape[1] // 2
        center_y = zoom_area.shape[0] // 2
        cv2.rectangle(zoom_area, (center_x - 2, center_y - 2), (center_x + 2, center_y + 2), (255, 0, 0), 1)

        zoom_image = Image.fromarray(zoom_area)
        zoom_photo = ImageTk.PhotoImage(zoom_image)
        zoom_label.config(image=zoom_photo)
        zoom_label.image = zoom_photo

    def on_mouse_up(event):
        end_x, end_y = event.x, event.y
        selection_window.destroy()
        zoom_window.destroy()
        # Show the main window again
        root.deiconify()
        # Save the selected coordinates
        save_coordinates(start_x, start_y, end_x, end_y)

    selection_canvas.bind("<ButtonPress-1>", on_mouse_down)
    selection_canvas.bind("<B1-Motion>", on_mouse_move)
    selection_canvas.bind("<ButtonRelease-1>", on_mouse_up)
    selection_window.bind("<Motion>", on_mouse_move)

def save_coordinates(start_x, start_y, end_x, end_y):
    data = {
        "start_x": start_x,
        "start_y": start_y,
        "end_x": end_x,
        "end_y": end_y,
    }
    with open("sweeper_coordinates.json", "w") as file:
        json.dump(data, file)

def save_grid_settings():
    data = {
        "rows": rows_entry.get(),
        "cols": cols_entry.get(),
        "cell_size": cell_size_entry.get()
    }
    print(data) # Debugging information
    with open("grid_settings.json", "w") as file:
        json.dump(data, file)
    

def analyze_area(root):
    def analyze():
        # Load the coordinates from the JSON file
        try:
            with open("sweeper_coordinates.json", "r") as file:
                data = json.load(file)
                region = (data["start_x"], data["start_y"], data["end_x"] - data["start_x"], data["end_y"] - data["start_y"])
        except FileNotFoundError:
            print("Please select an area first.")
            return

        # Clear old overlays
        if hasattr(root, 'current_overlays'):
            for overlay in root.current_overlays:
                overlay.destroy()
            root.current_overlays.clear()

        # Capture the screen area
        screenshot = capture_screen(region)
        processed_image = process_image(screenshot)
        board = analyze_board(processed_image, rows_entry, cols_entry)

        # Get the grid size from the input boxes
        try:
            rows = int(rows_entry.get())
            cols = int(cols_entry.get())
        except ValueError:
            print("Please enter valid numbers for rows and columns.")
            return

        # Draw grid lines on the image
        height, width, _ = processed_image.shape
        cell_width = width // cols
        cell_height = height // rows

        for i in range(1, rows):
            cv2.line(processed_image, (0, i * cell_height), (width, i * cell_height), (255, 0, 0), 1)
        for i in range(1, cols):
            cv2.line(processed_image, (i * cell_width, 0), (i * cell_width, height), (255, 0, 0), 1)

        # Convert the processed image to a format suitable for Tkinter
        processed_image_pil = Image.fromarray(processed_image)
        processed_image_tk = ImageTk.PhotoImage(processed_image_pil)


        if debug_var.get():
            # Display the image in the GUI
            image_label.config(image=processed_image_tk)
            image_label.image = processed_image_tk


        # Calculate and highlight bombs
        calculate_bombs(board, data["start_x"], data["start_y"], cell_width, cell_height, root)
    threading.Thread(target=analyze).start()

def open_template_window(root):
    # Create a new window for template generation
    template_window = tk.Toplevel(root)
    template_window.title("Generate Templates")

    # Create labels and entry fields for row and column
    row_label = tk.Label(template_window, text="Row:")
    row_label.pack(pady=5)
    row_entry = tk.Entry(template_window)
    row_entry.pack(pady=5)

    col_label = tk.Label(template_window, text="Column:")
    col_label.pack(pady=5)
    col_entry = tk.Entry(template_window)
    col_entry.pack(pady=5)

    # Create radio buttons for template type
    template_type_var = tk.StringVar(value="1")
    template_types = [
        ("1", "1-images/1-image.png"),
        ("2", "2-images/2-image.png"),
        ("3", "3-images/3-image.png"),
        ("4", "4-images/4-image.png"),
        ("5", "5-images/5-image.png"),
        ("6", "6-images/6-image.png"),
        ("7", "7-images/7-image.png"),
        ("8", "8-images/8-image.png"),
        ("Empty", "Empty/Empty.png"),
        ("Flag", "Flag/Flag.png"),
        ("Unopened", "Unopened/Unopened.png")
    ]

    for text, value in template_types:
        radio_button = tk.Radiobutton(template_window, text=text, variable=template_type_var, value=value)
        radio_button.pack(pady=5)

    # Create a button to save the template
    save_button = tk.Button(template_window, text="Save Template", command=lambda: save_template(row_entry.get(), col_entry.get(), template_type_var.get()))
    save_button.pack(pady=10)

def save_template(row, col, template_type):
    try:
        row = int(row)
        col = int(col)
    except ValueError:
        print("Invalid row or column value.")
        return

    # Load the coordinates from the JSON file
    try:
        with open("sweeper_coordinates.json", "r") as file:
            data = json.load(file)
            start_x = data["start_x"]
            start_y = data["start_y"]
            end_x = data["end_x"]
            end_y = data["end_y"]
    except FileNotFoundError:
        print("Please select an area first.")
        return

    # Get the grid size from the input boxes
    try:
        rows = int(rows_entry.get())
        cols = int(cols_entry.get())
        cell_size = int(cell_size_entry.get())
    except ValueError:
        print("Please enter valid numbers for rows, columns, and cell size.")
        return

    # Calculate cell width and height based on the new values
    cell_width = (end_x - start_x) // cols
    cell_height = (end_y - start_y) // rows

    # Capture the screen area
    screenshot = capture_screen((start_x, start_y, end_x - start_x, end_y - start_y))
    screenshot = np.array(screenshot)

    # Extract the specified cell from the screenshot
    cell = screenshot[row * cell_height:(row + 1) * cell_height, col * cell_width:(col + 1) * cell_width]

    # Save the cell as a template file
    template_path = f"C:/GitHubRepos/Sweeper-Analyzer/Templates/{template_type}"
    cv2.imwrite(template_path, cell)
    print(f"Template saved to {template_path}")

def get_board_size(root):
    # Hide the window to take a screenshot of full screen
    root.withdraw()
    time.sleep(0.2)  # Small delay to make sure the window is hidden

    # Take screenshot of the full screen
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

    # Convert the screenshot to grayscale
    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # Use edge detection to find the Minesweeper board
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Find contours in the edges
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour which should be the Minesweeper board
        largest_contour = max(contours, key=cv2.contourArea)

        # Get the bounding box of the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Set the coordinates
        start_x, start_y, end_x, end_y = x, y, x + w, y + h

        # Crop the capture area by 4 pixels on each side
        start_x += 4
        start_y += 4
        end_x -= 4
        end_y -= 4

        # Save the selected coordinates
        save_coordinates(start_x, start_y, end_x, end_y)

        # Get the cell size from the input box
        try:
            cell_size = int(cell_size_entry.get())
        except ValueError:
            print("Please enter a valid number for cell size.")
            root.deiconify()
            return

        # Try to determine the number of rows and columns
        rows = h // cell_size
        cols = w // cell_size

        # Update the rows and columns in the GUI
        rows_entry.delete(0, tk.END)
        rows_entry.insert(0, str(rows))
        cols_entry.delete(0, tk.END)
        cols_entry.insert(0, str(cols))

        print(f"Minesweeper board detected at coordinates: ({start_x}, {start_y}), ({end_x}, {end_y}) with {rows} rows and {cols} columns.")
    else:
        print("No Minesweeper board detected. Please try again.")

    # Show the main window again
    root.deiconify()

    save_grid_settings()

def clear_overlays(root):
    if hasattr(root, 'overlay'):
        root.canvas.delete("all")
        root.overlay.destroy()
        del root.overlay
    if hasattr(root, 'current_overlays'):
        for overlay in root.current_overlays:
            overlay.destroy()
        root.current_overlays.clear()

def auto_analyze(root):
    if auto_analyze_var.get():
        threading.Thread(target=analyze_area, args=(root,)).start()
        root.after(1000, lambda: auto_analyze(root))
