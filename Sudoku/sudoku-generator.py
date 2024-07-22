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

def create_pdf(puzzles, solutions, filename_puzzles, filename_solutions):
    c_puzzles = canvas.Canvas(filename_puzzles, pagesize=letter)
    c_solutions = canvas.Canvas(filename_solutions, pagesize=letter)
    width, height = letter
    margin = inch

    for i, (puzzle, solution) in enumerate(zip(puzzles, solutions)):
        draw_sudoku(c_puzzles, puzzle, width, height, margin)
        draw_sudoku(c_solutions, solution, width, height, margin)
        if i < len(puzzles) - 1:
            c_puzzles.showPage()
            c_solutions.showPage()
    
    c_puzzles.save()
    c_solutions.save()

def draw_sudoku(canvas, board, width, height, margin):
    cell_size = (width - 2 * margin) / 9
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
    
        create_pdf(puzzles, solutions, "sudoku_puzzles.pdf", "sudoku_solutions.pdf")
        print(f"{num_puzzles} Sudoku puzzles generated and saved successfully!")

    except ValueError:
        print("Invalid input. Please enter a valid number and difficulty level.")

if __name__ == "__main__":
    main()