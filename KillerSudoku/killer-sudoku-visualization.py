# This script is used for debugging
# It is used to visualize the Killer Sudoku cages
# It helps to visualize the location of the cages and 
# it ensures that there is no overlap

import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Grid size and spacing
grid_size = 9
cell_size = 40
total_size = grid_size * cell_size

# Create a plot
fig, ax = plt.subplots(figsize=(10, 10))
ax.set_xlim(0, total_size)
ax.set_ylim(0, total_size)
ax.set_aspect('equal')
ax.set_xticks([x * cell_size for x in range(grid_size + 1)])
ax.set_yticks([y * cell_size for y in range(grid_size + 1)])
ax.grid(True)

# Invert the y-axis to match the grid's top-left origin
ax.invert_yaxis()

# Example cages (same as provided)
cages = {
    1: [(8, 8), (7, 7), (7, 8)],
    2: [(8, 7), (8, 5), (8, 6)],
    3: [(6, 3), (6, 4)],
    4: [(6, 6), (6, 7), (6, 8)],
    5: [(2, 1), (1, 1), (2, 0), (3, 0), (1, 0)],
    6: [(5, 6), (5, 7), (5, 8)],
    7: [(4, 5)],
    8: [(4, 4), (5, 4)],
    9: [(7, 4), (7, 5), (7, 6), (6, 5)],
    10: [(2, 4), (1, 5), (2, 6), (2, 5), (3, 5)],
    11: [(1, 3)],
    12: [(2, 7), (3, 7), (1, 8), (1, 7), (2, 8)],
    13: [(0, 1), (0, 2), (0, 3), (0, 0)],
    14: [(6, 1), (5, 1), (5, 2)],
    15: [(8, 2), (8, 3), (8, 1)],
    16: [(6, 2), (7, 1), (7, 0), (7, 3), (7, 2)],
    17: [(0, 7), (0, 8)],
    18: [(1, 6), (0, 5), (0, 6)],
    19: [(4, 1)],
    20: [(3, 3), (3, 4), (4, 3)],
    21: [(4, 6), (4, 7), (4, 8)],
    22: [(3, 1), (3, 2), (4, 2), (2, 2)],
    23: [(8, 0)],
    24: [(2, 3)],
    25: [(4, 0), (5, 0), (6, 0)],
    26: [(1, 2)],
    27: [(5, 5)],
    28: [(0, 4), (1, 4)],
    29: [(8, 4)],
    30: [(3, 6)],
    31: [(3, 8)],
    32: [(5, 3)]
}

# Cage sums (for labeling)
cage_sums = {
    1: 12,
    2: 15,
    3: 9,
    4: 18,
    5: 24,
    6: 16,
    7: 7,
    8: 3,
    9: 26,
    10: 19,
    11: 6,
    12: 25,
    13: 21,
    14: 17,
    15: 11,
    16: 17,
    17: 15,
    18: 6,
    19: 3,
    20: 17,
    21: 12,
    22: 17,
    23: 9,
    24: 8,
    25: 19,
    26: 7,
    27: 6,
    28: 13,
    29: 7,
    30: 7,
    31: 9,
    32: 4
}

# Colors for cages
colors = plt.cm.get_cmap('tab20', len(cages))

# Plot each cage
for idx, (cage_id, cells) in enumerate(cages.items()):
    # Draw the cage cells
    for cell in cells:
        x, y = cell[1] * cell_size, cell[0] * cell_size
        rect = patches.Rectangle((x, y), cell_size, cell_size, linewidth=1, edgecolor='black', facecolor=colors(idx))
        ax.add_patch(rect)
    
    # Place the cage sum label
    label = str(cage_sums[cage_id])
    ax.text(cells[0][1] * cell_size + 2, cells[0][0] * cell_size + cell_size - 2, label, fontsize=12, color='black')

plt.show()
