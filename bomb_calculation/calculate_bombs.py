import numpy as np
from highlighting.highlight import highlight_cells

class Rule:
    def __init__(self, bomb_count, cells):
        self.bomb_count = bomb_count
        self.cells = set(cells)

def generate_rules(board):
    rows = len(board)
    cols = len(board[0])
    rules = []
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    for row in range(rows):
        for col in range(cols):
            if board[row][col].isdigit():
                num_bombs = int(board[row][col])
                unopened_neighbors = []
                for dr, dc in directions:
                    r, c = row + dr, col + dc
                    if 0 <= r < rows and 0 <= c < cols and board[r][c] in ["unopened", "flag"]:
                        unopened_neighbors.append((r, c))
                if unopened_neighbors:
                    rules.append(Rule(num_bombs, unopened_neighbors))
    return rules

def apply_rules(rules):
    guaranteed_bombs = set()
    certain_safe = set()
    rule_bombs = set()
    changes = True

    while changes:
        changes = False
        for rule in rules:
            if len(rule.cells) == rule.bomb_count:
                guaranteed_bombs.update(rule.cells)
                changes = True
            elif rule.bomb_count == 0:
                certain_safe.update(rule.cells)
                changes = True
        rules = [Rule(r.bomb_count - len(r.cells & guaranteed_bombs), r.cells - guaranteed_bombs - certain_safe) for r in rules]
        rules = [r for r in rules if r.cells]

    return guaranteed_bombs, certain_safe

def detect_1_2_1_pattern(board):
    rule_safe = set()
    rows = len(board)
    cols = len(board[0])
    found_pattern = False

    for row in range(1, rows - 1):
        for col in range(1, cols - 1):
            if board[row][col] == "2":
                # Check for vertical 1-2-1 pattern
                if board[row - 1][col] == "1" and board[row + 1][col] == "1":
                    # The unopened cells directly next to the '2' are always safe
                    if col - 1 >= 0 and board[row][col - 1] == "unopened":
                        rule_safe.add((row, col - 1))
                        found_pattern = True
                    if col + 1 < cols and board[row][col + 1] == "unopened":
                        rule_safe.add((row, col + 1))
                        found_pattern = True
                # Check for horizontal 1-2-1 pattern
                if board[row][col - 1] == "1" and board[row][col + 1] == "1":
                    # The unopened cells directly next to the '2' are always safe
                    if row - 1 >= 0 and board[row - 1][col] == "unopened":
                        rule_safe.add((row - 1, col))
                        found_pattern = True
                    if row + 1 < rows and board[row + 1][col] == "unopened":
                        rule_safe.add((row + 1, col))
                        found_pattern = True

    if not found_pattern:
        print("Debug: No 1-2-1 pattern found.")

    return rule_safe

def detect_1_2_2_1_pattern(board):
    rule_safe = set()
    rows = len(board)
    cols = len(board[0])
    found_pattern = False

    for row in range(1, rows - 2):
        for col in range(1, cols - 1):
            if board[row][col] == "2" and board[row + 1][col] == "2":
                # Check for vertical 1-2-2-1 pattern
                if board[row - 1][col] == "1" and board[row + 2][col] == "1":
                    # The unopened cells directly next to the '1's are always safe
                    if col - 1 >= 0 and board[row - 1][col - 1] == "unopened":
                        rule_safe.add((row - 1, col - 1))
                        found_pattern = True
                    if col + 1 < cols and board[row - 1][col + 1] == "unopened":
                        rule_safe.add((row - 1, col + 1))
                        found_pattern = True
                    if col - 1 >= 0 and board[row + 2][col - 1] == "unopened":
                        rule_safe.add((row + 2, col - 1))
                        found_pattern = True
                    if col + 1 < cols and board[row + 2][col + 1] == "unopened":
                        rule_safe.add((row + 2, col + 1))
                        found_pattern = True

                # Check for horizontal 1-2-2-1 pattern
                if board[row][col - 1] == "1" and board[row][col + 2] == "1":
                    # The unopened cells directly next to the '1's are always safe
                    if row - 1 >= 0 and board[row - 1][col - 1] == "unopened":
                        rule_safe.add((row - 1, col - 1))
                        found_pattern = True
                    if row + 1 < rows and board[row + 1][col - 1] == "unopened":
                        rule_safe.add((row + 1, col - 1))
                        found_pattern = True
                    if row - 1 >= 0 and board[row - 1][col + 2] == "unopened":
                        rule_safe.add((row - 1, col + 2))
                        found_pattern = True
                    if row + 1 < rows and board[row + 1][col + 2] == "unopened":
                        rule_safe.add((row + 1, col + 2))
                        found_pattern = True

    if not found_pattern:
        print("Debug: No 1-2-2-1 pattern found.")
    # Remove any cells that are guaranteed bombs from the set of safe cells
    return rule_safe

def detect_1_1_pattern(board, guaranteed_bombs):
    rule_safe = set()
    rows = len(board)
    cols = len(board[0])

    # Check for horizontal 1-1 pattern
    for row in range(rows):
        for col in range(cols - 1):
            if board[row][col] == "1" and board[row][col + 1] == "1":
                # Find unopened cells directly adjacent to '1' tiles
                if col - 1 >= 0 and board[row][col - 1] == "unopened":
                    rule_safe.add((row, col - 1))
                if col + 2 < cols and board[row][col + 2] == "unopened":
                    rule_safe.add((row, col + 2))

    # Check for vertical 1-1 pattern
    for col in range(cols):
        for row in range(rows - 1):
            if board[row][col] == "1" and board[row + 1][col] == "1":
                # Find unopened cells directly adjacent to '1' tiles
                if row - 1 >= 0 and board[row - 1][col] == "unopened":
                    rule_safe.add((row - 1, col))
                if row + 2 < rows and board[row + 2][col] == "unopened":
                    rule_safe.add((row + 2, col))

    # Remove any cells that are guaranteed bombs from the set of safe cells
    rule_safe -= guaranteed_bombs

    return rule_safe

def calculate_bombs(board, start_x, start_y, cell_width, cell_height, root):
    rules = generate_rules(board)
    guaranteed_bombs, certain_safe = apply_rules(rules)
    rule_safe_1_2_1 = detect_1_2_1_pattern(board)
    rule_safe_1_2_2_1 = detect_1_2_2_1_pattern(board)
    rule_safe_1_1 = detect_1_1_pattern(board, guaranteed_bombs)

    # Highlight all the safe cells identified by 1-2-1 pattern in yellow
    highlight_cells(list(rule_safe_1_2_1), start_x, start_y, cell_width, cell_height, root, 'yellow')
    # Highlight all the safe cells identified by 1-2-2-1 pattern in orange
    highlight_cells(list(rule_safe_1_2_2_1), start_x, start_y, cell_width, cell_height, root, 'orange')
    # Highlight all the safe cells identified by 1-1 pattern in blue
    highlight_cells(list(rule_safe_1_1), start_x, start_y, cell_width, cell_height, root, 'blue')
    # Highlight all the guaranteed bombs on the screen in red
    #highlight_cells(list(guaranteed_bombs), start_x, start_y, cell_width, cell_height, root, 'red')
    #Highlight all the safe cells on the screen in green
    highlight_cells(list(certain_safe), start_x, start_y, cell_width, cell_height, root, 'green')
