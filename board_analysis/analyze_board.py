import cv2
import numpy as np

# Load template images
templates = {
    "1": cv2.imread("C:/GitHubRepos/Sweeper-Analyzer/Templates/1-images/1-image.png"),
    "2": cv2.imread("C:/GitHubRepos/Sweeper-Analyzer/Templates/2-images/2-image.png"),
    "3": cv2.imread("C:/GitHubRepos/Sweeper-Analyzer/Templates/3-images/3-image.png"),
    "4": cv2.imread("C:/GitHubRepos/Sweeper-Analyzer/Templates/4-images/4-image.png"),
    "5": cv2.imread("C:/GitHubRepos/Sweeper-Analyzer/Templates/5-images/5-image.png"),
    "6": cv2.imread("C:/GitHubRepos/Sweeper-Analyzer/Templates/6-images/6-image.png"),
    # "7": cv2.imread("C:/GitHubRepos/Sweeper-Analyzer/Templates/7-images/7-image.png"),
    # "8": cv2.imread("C:/GitHubRepos/Sweeper-Analyzer/Templates/8-images/8-image.png"),
    "empty": cv2.imread("C:/GitHubRepos/Sweeper-Analyzer/Templates/Empty/Empty.png"),
    "flag": cv2.imread("C:/GitHubRepos/Sweeper-Analyzer/Templates/Flag/Flag.png"),
    "unopened": cv2.imread("C:/GitHubRepos/Sweeper-Analyzer/Templates/Unopened/Unopened.png")
}

def analyze_board(processed_image, rows_entry, cols_entry):
    # Assume the processed image is a color image of the Minesweeper board
    height, width, _ = processed_image.shape

    # Get the grid size from the input boxes
    try:
        rows = int(rows_entry.get())
        cols = int(cols_entry.get())
    except ValueError:
        print("Please enter valid numbers for rows and columns.")
        return []

    cell_width = width // cols
    cell_height = height // rows

    board = []

    for row in range(rows):
        board_row = []
        for col in range(cols):
            # Extract the cell from the image
            cell = processed_image[row * cell_height:(row + 1) * cell_height, col * cell_width:(col + 1) * cell_width]
            
            # Analyze the cell to determine its contents
            cell_value, best_score = analyze_cell(cell)
            board_row.append(cell_value)
            
            # Draw the prediction on the image
            if cell_value == "unknown":
                text = "?"
            else:
                text = cell_value[0].upper() if cell_value in ["empty", "unopened", "flag"] else cell_value
            text_position = (col * cell_width + cell_width // 2 - 10, row * cell_height + cell_height // 2 + 10)
            cv2.putText(processed_image, text, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            
            # Debugging information
            #print(f"Cell ({row}, {col}): {cell_value} (Score: {best_score})")
        
        board.append(board_row)
    
    return board

def analyze_cell(cell):
    # Perform template matching for each template using the original template size
    results = {}
    for key, template in templates.items():
        res = cv2.matchTemplate(cell, template, cv2.TM_SQDIFF_NORMED)
        min_val, _, _, _ = cv2.minMaxLoc(res)
        results[key] = min_val

    # Find the template with the lowest matching score
    best_match = min(results, key=results.get)
    best_score = results[best_match]

    return best_match, best_score

