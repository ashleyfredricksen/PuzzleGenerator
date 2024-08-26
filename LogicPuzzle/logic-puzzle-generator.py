import json
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Frame

def load_config(filename='config.json'):
    with open(filename, 'r') as file:
        return json.load(file)

def read_names(filename):
    with open(filename, 'r') as file:
        names = [line.strip() for line in file]
    return names

def select_names(names, num=5):
    return random.sample(names, num)

def generate_categories(config, difficulty):
    category_names = list(config['categories'].keys())
    difficulty_levels = {
        'easy': 2,
        'medium': 3,
        'hard': 3
    }
    num_categories = difficulty_levels.get(difficulty, 2)
    return random.sample(category_names, num_categories)

def generate_items(config, names, categories):
    num_items = len(names)
    items = []
    
    for category in categories:
        category_items = config['categories'].get(category, [])

        # Check if num_items_per_category is more than available items
        if num_items > len(category_items):
            raise ValueError(f"Requested number of items for category '{category}' exceeds available items.")
        
        # Randomly sample items from the category
        sampled_items = random.sample(category_items, num_items)

        # Add sampled items to the result dictionary
        items.extend(sampled_items)

    return items

def get_clue_distributions(difficulty):
    distributions = {
        'easy': {
            'positive': 70,
            'negative': 20,
            'exclusive': 10
        },
        'medium': {
            'positive': 50,
            'negative': 30,
            'exclusive': 20
        },
        'hard': {
            'positive': 30,
            'negative': 40,
            'exclusive': 30
        }
    }

    return distributions.get(difficulty, distributions['easy'])

def generate_clues(config, names, categories, difficulty):
    distributions = get_clue_distributions(difficulty)
    num_clues = 10

    # Determine how many clues of each type
    num_positive = int(num_clues * distributions['positive'] / 100)
    num_negative = int(num_clues * distributions['negative'] / 100)
    num_exclusive = num_clues - (num_positive + num_negative)

    clue_types = {
        'positive': config['clue_templates']['positive'],
        'negative': config['clue_templates']['negative'],
        'exclusive': config['clue_templates']['exclusive']
    }

    clues = []

    # Function to generate a single clue
    def generate_single_clue(clue_type):
        template = random.choice(clue_types[clue_type])
        name1, name2 = random.sample(names, 2)
        category = random.choice(categories)
        values = config['categories'].get(category, [])

        if len(values) > 1:
            item1 = random.choice(values)
            item2 = random.choice([v for v in values if v != item1])
        elif values:
            item1 = values[0]
            item2 = "Unknown"
        else:
            item1 = "Unknown"
            item2 = "Unknown"

        context = {
            'name1': name1,
            'name2': name2,
            'item1': item1,
            'item2': item2,
            'category': category
        }

        try:
            clue = template.format(**context)
        except KeyError as e:
            print(f"KeyError: Missing key '{e.args[0]}' in template '{template}'")
            clue = template

        return clue

    # Generate clues according to distribution
    for _ in range(num_positive):
        clues.append(f"{generate_single_clue('positive')}")
    for _ in range(num_negative):
        clues.append(f"{generate_single_clue('negative')}")
    for _ in range(num_exclusive):
        clues.append(f"{generate_single_clue('exclusive')}")

    random.shuffle(clues)
    return clues

def draw_grid(canvas, categories, items, cell_size=30, x_start=100, y_start=650):
    num_categories = len(categories)
    items_per_category = 5 #len(items) // num_categories

    # Calculate total grid size (for the overall grid containing all subgrids)
    total_grid_width = items_per_category * cell_size * (num_categories - 1)
    total_grid_height = items_per_category * cell_size * (num_categories - 1)

    # Adjust the position and size to fit on the page
    x_start = (letter[0] - total_grid_width) / 2
    y_start = (letter[1] + total_grid_height) / 2 + 250

    # Draw subgrids
    for row_category_idx in range(num_categories - 1, 0, -1):
        for col_category_idx in range(row_category_idx):
            subgrid_x_start = x_start + col_category_idx * items_per_category * cell_size
            subgrid_y_start = y_start - (num_categories - row_category_idx) * items_per_category * cell_size

            # Draw subgrid lines
            for i in range(items_per_category + 1):
                canvas.setLineWidth(1)
                # Vertical lines within the subgrid
                canvas.line(subgrid_x_start + i * cell_size, subgrid_y_start, 
                       subgrid_x_start + i * cell_size, subgrid_y_start - items_per_category * cell_size)
                # Horizontal lines within the subgrid
                canvas.line(subgrid_x_start, subgrid_y_start - i * cell_size, 
                       subgrid_x_start + items_per_category * cell_size, subgrid_y_start - i * cell_size)
    
            # Draw thicker borders for the subgrid
            canvas.setLineWidth(2)
            canvas.rect(subgrid_x_start, subgrid_y_start - items_per_category * cell_size, 
                   items_per_category * cell_size, items_per_category * cell_size)

def draw_solution(canvas, categories, items, correct_answers, cell_size=30, x_start=100, y_start=650):
    # Draw grid with TRUE and FALSE markers
    draw_grid(canvas, categories, items, cell_size, x_start, y_start)

    # Mark correct answers with circles
    canvas.setFillColorRGB(0, 0, 0) # Fill color for dots
    for (row, col) in correct_answers: 
        x = x_start + col * cell_size + cell_size / 2
        y = y_start - row * cell_size + cell_size / 2
        canvas.circle(x, y, 10, fill=True)

    # # Optionally mark FALSE with X
    # canvas.setStrokeColorRGB(1, 0, 0)  # Set color for X marks
    # canvas.setLineWidth(1)
    # for (row, col) in correct_answers:
    #     x = x_start + col * cell_size
    #     y = y_start - row * cell_size
    #     canvas.line(x, y, x + cell_size, y - cell_size)  # Draw X
    #     canvas.line(x + cell_size, y, x, y - cell_size)

def create_pdf(categories, items, clues, correct_answers, c_puzzles, c_solutions):
    draw_grid(c_puzzles, categories, items)
    draw_solution(c_solutions, categories, items, correct_answers)

    # Add clues below the puzzle grid
    style = ParagraphStyle('default', fontSize=12, leading=14)
    numbered_clues = [Paragraph(f"{i+1}. {clue}", style) for i, clue in enumerate(clues)]
    
    frame = Frame(100, 100, letter[0] - 200, 150, showBoundary=0)
    story = numbered_clues
    frame.addFromList(story, c_puzzles)

    c_puzzles.showPage()
    c_solutions.showPage()

def main():
    config = load_config()
    names = read_names('names.txt')

    num_puzzles = int(input("Enter number of puzzles to generate: "))
    difficulty = input("Enter difficulty level (easy, medium, hard): ").strip().lower()

    c_puzzles = canvas.Canvas("logic_puzzles.pdf", pagesize=letter)
    c_solutions = canvas.Canvas("logic_solutions.pdf", pagesize=letter)

    for _ in range(num_puzzles):
        selected_names = select_names(names)
        categories_without_names = generate_categories(config, difficulty)
        categories = ["Names"] + categories_without_names
        items = selected_names + generate_items(config, selected_names, categories_without_names)
        clues = generate_clues(config, selected_names, categories_without_names, difficulty)

        print(categories)
        print(selected_names)
        print(items)    
        print(clues)

        # Generate and save solution
        correct_answers = {(0, 1), (1, 2)}  # Example correct answers; update based on actual solution
        
        # Generate and save puzzle
        create_pdf(categories, items, clues, correct_answers, c_puzzles, c_solutions)
    
    c_puzzles.save()
    c_solutions.save()

if __name__ == "__main__":
    main()
