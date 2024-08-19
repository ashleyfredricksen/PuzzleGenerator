import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def generate_sudoku(difficulty):
    base = 3
    side = base * base

    # Pattern for a baseline valid solution
    def pattern(r, c): return (base*(r % base) + r // base + c) % side

    # Randomize rows, columns, and numbers of valid base pattern
    def shuffle(s): return random.sample(s, len(s))
    rBase = range(base)
    rows = [g * base + r for g in shuffle(rBase) for r in shuffle(rBase)]
    cols = [g * base + c for g in shuffle(rBase) for c in shuffle(rBase)]
    nums = shuffle(range(1, base * base + 1))

    # Produce board using randomized baseline pattern
    board = [[nums[pattern(r,c)] for c in cols] for r in rows]

    # Determine number of empty squares based on difficulty
    if difficulty == 'easy':
        no_of_holes = random.randint(28, 36)
    elif difficulty == 'medium':
        no_of_holes == random.randint(37,45)
    elif difficulty == 'hard':
        no_of_holes == random.randint(46, 54)
    else:
        raise ValueError("Invalid difficulty level")

    squares = side * side
    for p in random.sample(range(squares), no_of_holes):
        board[p // side][p % side] = 0
    
    return board, solve_sudoku([row[:] for row in board])

def solve_sudoku(board):
    side = len(board)

    def find_empty_location(board):
        for row in range(side):
            for col in range(side):
                if board[row][col] == 0:
                    return row, col
        return None
    
    def is_safe(board, row, col, num):
        for x in range(side):
            if board[row][x] == num or board[x][col] == num:
                return False
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
                    return False
        return True
    
    def solve(board):
        empty_loc = find_empty_location(board)
        if not empty_loc:
            return True
        row, col = empty_loc
        for num in range(1, side + 1):
            if is_safe(board, row, col, num):
                board[row][col] = num
                if solve(board):
                    return True
                board[row][col] = 0
        return False
    
    solve(board)
    return board

def generate_cages(solution_board):
    side = len(solution_board)
    cages = []
    visited_cells = set()
    cage_id = 1

    while len(visited_cells) < side * side:
        cage_size = random.randint(1, 5)  # Adjust size as needed
        cage_cells = set()
        cage_numbers = set()

        # Randomly pick a starting cell that has not been visited
        start_row, start_col = random.randint(0, side - 1), random.randint(0, side - 1)
        if (start_row, start_col) in visited_cells:
            continue
        cage_cells.add((start_row, start_col))
        cage_numbers.add(solution_board[start_row][start_col])

        # Use a list to explore adjacent cells and form a cage
        stack = [(start_row, start_col)]
        while stack and len(cage_cells) < cage_size:
            r, c = stack.pop()
            for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nr, nc = r + dr, c + dc
                if (0 <= nr < side and 0 <= nc < side and (nr, nc) not in visited_cells
                        and (nr, nc) not in cage_cells and solution_board[nr][nc] not in cage_numbers):
                    cage_cells.add((nr, nc))
                    cage_numbers.add(solution_board[nr][nc])
                    stack.append((nr, nc))
                    if len(cage_cells) == cage_size:
                        break

        if cage_cells:
            cage_sum = sum(solution_board[r][c] for r, c in cage_cells)
            cages.append({'id': cage_id, 'cells': list(cage_cells), 'sum': cage_sum})
            visited_cells.update(cage_cells)
            cage_id += 1

    return cages

def create_pdf(puzzles, solutions, filename_puzzles, filename_solutions):
    c_puzzles = canvas.Canvas(filename_puzzles, pagesize=letter)
    c_solutions = canvas.Canvas(filename_solutions, pagesize=letter)
    width, height = letter
    margin = inch

    for i, (puzzle, solution) in enumerate(zip(puzzles, solutions)):
        cages = generate_cages(solution)
        draw_sudoku(c_puzzles, puzzle, solution, cages, width, height, margin)
        draw_sudoku(c_solutions, solution, solution, cages, width, height, margin)
        if i < len(puzzles) - 1:
            c_puzzles.showPage()
            c_solutions.showPage()
    
    c_puzzles.save()
    c_solutions.save()

def draw_sudoku(canvas, board, solution, cages, width, height, margin):
    cell_size = (width - 2 * margin) / 9
    cage_thickness = 2  # Adjust as needed for cage line thickness
    inset = 2

    # Debugging: Use colors for cages, similar to the visualization script
    colors = [
        (1, 0, 0), (0, 1, 0), (0, 0, 1),  # RGB for basic colors
        (1, 1, 0), (0, 1, 1), (1, 0, 1),  # RGB for mixed colors
        (0.5, 0.5, 0.5)  # Grey for fallback
    ]

    # Draw cells and numbers
    for i in range(9):
        for j in range(9):
            x = margin + j * cell_size
            y = height - margin - (i + 1) * cell_size
            canvas.rect(x, y, cell_size, cell_size)
            if board[i][j] != 0:
                canvas.drawString(x + cell_size / 2.5, y + cell_size / 3, str(board[i][j]))

    # Draw thicker lines for the 3x3 sub-grids
    for i in range(10):
        line_width = 2 if i % 3 == 0 else 1
        canvas.setLineWidth(line_width)
        canvas.line(margin, height - margin - i * cell_size, margin + 9 * cell_size, height - margin - i * cell_size)
        canvas.line(margin + i * cell_size, height - margin, margin + i * cell_size, height - margin - 9 * cell_size)

    # Draw cages around cells with the same sum constraint (for Killer Sudoku)
    for cage in cages:
        canvas.setStrokeColorRGB(0, 0, 0)  # Set color to black
        canvas.setLineWidth(cage_thickness)
        canvas.setDash(0.5, 2) # Set dashed line pattern (1pt line, 2pt space)

        for (r, c) in cage['cells']:
            x1 = margin + c * cell_size + inset
            y1 = height - margin - (r + 1) * cell_size + inset
            x2 = margin + (c + 1) * cell_size - inset
            y2 = height - margin - r * cell_size - inset

            # Draw cage borders, inset from the cell border
            if (r, c-1) not in cage['cells']:
                canvas.line(x1, y1, x1, y2)  # Left border
            if (r, c+1) not in cage['cells']:
                canvas.line(x2, y1, x2, y2)  # Right border
            if (r-1, c) not in cage['cells']:
                canvas.line(x1, y2, x2, y2)  # Top border
            if (r+1, c) not in cage['cells']:
                canvas.line(x1, y1, x2, y1)  # Bottom border

        # Debug: Print the calculated coordinates for the cage. 
        # Use values in killer-sudoku-visualization.py
        
        print(f"{cage['id']}: {cage['cells']},")
        print(f"{cage['id']}: {cage['sum']},")     
        
        # Draw the sum of the cage at the top-left of the cage
        first_cell = min(cage['cells'], key=lambda cell: (cell[0], cell[1]))  # Top-left cell of the cage
        sum_x = margin + first_cell[1] * cell_size + 4
        sum_y = height - margin - (first_cell[0] + 1) * cell_size + cell_size - 10
        canvas.setFont("Helvetica", 8)
        canvas.setStrokeColorRGB(0, 0, 0)
        canvas.setFillColorRGB(0, 0, 0)
        canvas.drawString(sum_x, sum_y, str(cage['sum']))

    # Reset color to black for further drawing
    canvas.setStrokeColorRGB(0, 0, 0)

def main():
    try:
        num_puzzles = int(input("Enter number of puzzles to generate: "))
        difficulty = input("Enter difficulty level (easy, medium, hard): ").strip().lower()

        puzzles = []
        solutions = []

        for _ in range(num_puzzles):
            puzzle, solution = generate_sudoku(difficulty)
            puzzles.append(puzzle)
            solutions.append(solution)
    
        create_pdf(puzzles, solutions, "killer_sudoku_puzzles5.pdf", "killer_sudoku_solutions5.pdf")
        print(f"{num_puzzles} Sudoku puzzles generated and saved successfully!")

    except ValueError:
        print("Invalid input. Please enter a valid number and difficulty level.")

if __name__ == "__main__":
    main()