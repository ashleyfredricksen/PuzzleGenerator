import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import random

def read_words(filename, num_words=15):
    with open(filename, 'r') as file:
        words = file.read().splitlines()
    words = [word.upper() for word in words]
    return random.sample(words, num_words)

def create_word_search(words, size=15):
    grid = np.full((size, size), '', dtype='<U1')
    word_positions = []  # To store the positions of words
    
    def can_place_word(word, row, col, direction):
        if direction == 'H':
            if col + len(word) > size:
                return False
            for i in range(len(word)):
                if grid[row, col + i] not in ('', word[i]):
                    return False
        elif direction == 'V':
            if row + len(word) > size:
                return False
            for i in range(len(word)):
                if grid[row + i, col] not in ('', word[i]):
                    return False
        return True

    def place_word(word, row, col, direction):
        positions = []
        if direction == 'H':
            for i in range(len(word)):
                grid[row, col + i] = word[i]
                positions.append((row, col + i))
        elif direction == 'V':
            for i in range(len(word)):
                grid[row + i, col] = word[i]
                positions.append((row + i, col))
        return positions

    directions = ['H', 'V']
    for word in words:
        placed = False
        while not placed:
            direction = random.choice(directions)
            row = random.randint(0, size - 1)
            col = random.randint(0, size - 1)
            if can_place_word(word, row, col, direction):
                positions = place_word(word, row, col, direction)
                word_positions.append((word, positions))
                placed = True

    grid[grid == ''] = random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=np.sum(grid == ''))
    return grid, word_positions

def save_to_pdf(grid, words, filename, word_positions=None, include_word_list=True):
    from reportlab.lib.pagesizes import letter
    doc_width, doc_height = letter
    cell_size = 26
    font_size = 20
    word_font_size = 16
    max_col_width = 2 * inch  # Width for each column of words
    padding = 5  # Padding between lines
    
    grid_size = len(grid)
    grid_width = cell_size * grid_size
    grid_height = cell_size * grid_size
    
    start_x = (doc_width - grid_width) / 2
    start_y = (doc_height + grid_height) / 2
    
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Courier", font_size)  # Use a monospaced font
    
    # Write grid to PDF
    for i, row in enumerate(grid):
        for j, letter in enumerate(row):
            c.drawString(start_x + j * cell_size, start_y - i * cell_size, letter)
    
    # Highlight words if word_positions is provided
    if word_positions:
        c.setStrokeColorRGB(0, 0, 0)  # Black color for outlining the word
        c.setLineWidth(2)
        for word, positions in word_positions:
            start_pos = positions[0]
            end_pos = positions[-1]
            start_x_pos = start_x + start_pos[1] * cell_size
            start_y_pos = start_y - start_pos[0] * cell_size
            end_x_pos = start_x + end_pos[1] * cell_size
            end_y_pos = start_y - end_pos[0] * cell_size

            if start_pos[0] == end_pos[0]:  # Horizontal word
                c.rect(start_x_pos - 6, start_y_pos - font_size + 14, cell_size * len(word), font_size + 2, fill=0)
            else:  # Vertical word
                c.rect(start_x_pos - 6, end_y_pos + 14 - cell_size, cell_size, cell_size * len(word), fill=0)

    # Write list of words if include_word_list is True
    if include_word_list:
        word_list_height = (len(words) * (word_font_size + padding)) / 2  # Estimate height needed
        word_list_y = start_y - grid_height - word_list_height - 20  # Add some padding
        c.setFont("Helvetica", word_font_size)
        x = start_x
        y = word_list_y + word_list_height
        col_width = max_col_width
        words_per_col = int(word_list_height / (word_font_size + padding))
        
        for i, word in enumerate(words):
            if i > 0 and i % words_per_col == 0:
                x += col_width
                y = word_list_y + word_list_height
            c.drawString(x, y - (i % words_per_col) * (word_font_size + padding), word)
    
    c.save()

def main():
    words = read_words('words.txt')
    sorted_words = sorted(words) # sort the words in alphabetical order
    grid, word_positions = create_word_search(words)
    save_to_pdf(grid, sorted_words, 'word_search.pdf')
    save_to_pdf(grid, sorted_words, 'word_search_solution.pdf', word_positions=word_positions, include_word_list=False)

if __name__ == '__main__':
    main()
