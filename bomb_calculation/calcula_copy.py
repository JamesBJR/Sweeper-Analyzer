import numpy as np
from highlighting.highlight import highlight_cells

def calculate_bombs(board, start_x, start_y, cell_width, cell_height, root):
    """
    Calculate the locations of bombs on the Minesweeper board and highlight them on the screen.
    
    Args:
        board (list of list of str): The Minesweeper board represented as a 2D list.
                                     Each cell contains a string representing the cell content:
                                     - "1" to "8" for numbers
                                     - "empty" for empty cells
                                     - "flag" for flagged cells
                                     - "unopened" for unopened cells
        start_x (int): The starting x-coordinate of the grid.
        start_y (int): The starting y-coordinate of the grid.
        cell_width (int): The width of each cell in the grid.
        cell_height (int): The height of each cell in the grid.
        root (tk.Tk): The root Tkinter window.
    """

    rows = len(board)
    cols = len(board[0])
    bombs = []
    chordable_cells = []
    pattern_bombs = []
    pattern_safe = []

    # Define the directions for the 8 neighboring cells
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for row in range(rows):
        for col in range(cols):
            if board[row][col].isdigit():
                num_bombs = int(board[row][col])
                unopened_neighbors = []
                flagged_neighbors = 0
                for dr, dc in directions:
                    r, c = row + dr, col + dc
                    if 0 <= r < rows and 0 <= c < cols:
                        if board[r][c] in ["unopened", "flag"]:
                            unopened_neighbors.append((r, c))
                        if board[r][c] == "flag":
                            flagged_neighbors += 1
                if flagged_neighbors == num_bombs and any(board[r][c] == "unopened" for r, c in unopened_neighbors):
                    chordable_cells.append((row, col))
                if len(unopened_neighbors) == num_bombs:
                    bombs.extend(unopened_neighbors)

                # Determine safe squares to add to the pattern_safe list without using flag information
                known_bombs = [(r, c) for r, c in unopened_neighbors if (r, c) in bombs or (r, c) in pattern_bombs]
                if len(known_bombs) == num_bombs:
                    for r, c in unopened_neighbors:
                        if (r, c) not in bombs and (r, c) not in pattern_bombs:
                            pattern_safe.append((r, c))

                # Detect the 1-2-1 pattern and mark the bombs touching the 1s
                if board[row][col] == "2":
                    # Check for horizontal 1-2-1 pattern
                    if col > 0 and col < cols - 1:
                        if board[row][col - 1] == "1" and board[row][col + 1] == "1":
                            # Mark the unopened cells adjacent to the 1s as bombs
                            for dr, dc in [(-1, 0), (1, 0)]:
                                r1, c1 = row + dr, col - 1 + dc
                                r2, c2 = row + dr, col + 1 + dc
                                if 0 <= r1 < rows and 0 <= c1 < cols and board[r1][c1] == "unopened":
                                    pattern_bombs.append((r1, c1))
                                if 0 <= r2 < rows and 0 <= c2 < cols and board[r2][c2] == "unopened":
                                    pattern_bombs.append((r2, c2))
                    # Check for vertical 1-2-1 pattern
                    if row > 0 and row < rows - 1:
                        if board[row - 1][col] == "1" and board[row + 1][col] == "1":
                            # Mark the unopened cells adjacent to the 1s as bombs
                            for dr, dc in [(0, -1), (0, 1)]:
                                r1, c1 = row - 1 + dr, col + dc
                                r2, c2 = row + 1 + dr, col + dc
                                if 0 <= r1 < rows and 0 <= c1 < cols and board[r1][c1] == "unopened":
                                    pattern_bombs.append((r1, c1))
                                if 0 <= r2 < rows and 0 <= c2 < cols and board[r2][c2] == "unopened":
                                    pattern_bombs.append((r2, c2))

                # Detect the 1-2-2-1 pattern and mark the bombs touching the 2s
                if board[row][col] == "2":
                    # Check for horizontal 1-2-2-1 pattern
                    if col > 1 and col < cols - 2:
                        if board[row][col - 2] == "1" and board[row][col - 1] == "2" and board[row][col + 1] == "2" and board[row][col + 2] == "1":
                            # Mark the unopened cells adjacent to the 2s as bombs
                            for dr, dc in [(0, -1), (0, 1)]:
                                r1, c1 = row + dr, col - 1 + dc
                                r2, c2 = row + dr, col + 1 + dc
                                if 0 <= r1 < rows and 0 <= c1 < cols and board[r1][c1] == "unopened":
                                    pattern_bombs.append((r1, c1))
                                if 0 <= r2 < rows and 0 <= c2 < cols and board[r2][c2] == "unopened":
                                    pattern_bombs.append((r2, c2))
                    # Check for vertical 1-2-2-1 pattern
                    if row > 1 and row < rows - 2:
                        if board[row - 2][col] == "1" and board[row - 1][col] == "2" and board[row + 1][col] == "2" and board[row + 2][col] == "1":
                            # Mark the unopened cells adjacent to the 2s as bombs
                            for dr, dc in [(-1, 0), (1, 0)]:
                                r1, c1 = row + dr, col + dc
                                r2, c2 = row + dr, col + dc
                                if 0 <= r1 < rows and 0 <= c1 < cols and board[r1][c1] == "unopened":
                                    pattern_bombs.append((r1, c1))
                                if 0 <= r2 < rows and 0 <= c2 < cols and board[r2][c2] == "unopened":
                                    pattern_bombs.append((r2, c2))

                # Detect the 1-1-X pattern and mark the safe cell
                if board[row][col] == "1":
                    # Check for horizontal 1-1-X pattern
                    if col < cols - 2:
                        if board[row][col + 1] == "1" and board[row][col + 2] == "unopened":
                            pattern_safe.append((row, col + 2))
                    # Check for vertical 1-1-X pattern
                    if row < rows - 2:
                        if board[row + 1][col] == "1" and board[row + 2][col] == "unopened":
                            pattern_safe.append((row + 2, col))

    # Remove duplicates
    bombs = list(set(bombs))
    chordable_cells = list(set(chordable_cells))
    pattern_bombs = list(set(pattern_bombs))
    pattern_safe = list(set(pattern_safe))
    
    # Highlight the bombs on the screen
    highlight_cells(bombs, start_x, start_y, cell_width, cell_height, root, 'red')
    # Highlight the chordable cells on the screen
    highlight_cells(chordable_cells, start_x, start_y, cell_width, cell_height, root, 'blue')
    # Highlight the pattern bombs on the screen
    highlight_cells(pattern_bombs, start_x, start_y, cell_width, cell_height, root, 'yellow')
    # Highlight the pattern safe cells on the screen
    highlight_cells(pattern_safe, start_x, start_y, cell_width, cell_height, root, 'green')
