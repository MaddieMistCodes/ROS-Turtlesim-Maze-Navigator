#!/usr/bin/env python3

# 1 = wall 0 = space

import random

# Grid Constraints

CELL_SIZE = 1.0 # one grid cell = 1.0 in turtlesim unit
ORIGIN_X = 1.0
ORIGIN_Y = 1.0
GRID_ROWS = 9
GRID_COLS = 9

# Maze Definition

MAZE_1 = {
	'name': 'FalseTrap',
	'grid': [
		[1, 1, 1, 1, 1, 1, 1, 1, 1],
		[1, 0, 0, 0, 1, 0, 0, 0, 1],
		[1, 0, 1, 0, 1, 0, 1, 0, 1],
		[1, 0, 1, 0, 0, 0, 1, 0, 1],
		[1, 0, 1, 1, 1, 0, 1, 0, 1],
		[1, 0, 0, 0, 1, 0, 1, 0, 1],
		[1, 1, 1, 0, 1, 1, 1, 0, 1],
		[1, 0, 0, 0, 0, 0, 1, 0, 1],
		[1, 1, 1, 1, 1, 1, 1, 1, 1],

		],
		'start': (7, 1),
		'goal': (5, 5),
}
MAZE_2 = {
        'name': 'TrapCorridor',
        'grid': [
                [1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 1, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 1, 0, 0, 0, 1, 0, 1],
                [1, 0, 1, 1, 1, 0, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 1, 0, 1],
                [1, 1, 1, 1, 1, 0, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 1, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1],

                ],
                'start': (7, 1),
                'goal': (1, 1),
}
MAZE_3 = {
        'name': 'PoorTurtle',
        'grid': [
                [1, 1, 1, 1, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 1, 0, 1],
                [1, 1, 1, 0, 1, 0, 1, 0, 1],
                [1, 0, 0, 0, 0, 0, 1, 0, 1],
                [1, 0, 1, 0, 1, 0, 1, 0, 1],
                [1, 1, 1, 0, 0, 0, 0, 0, 1],
                [1, 0, 1, 0, 1, 1, 1, 1, 1],
                [1, 0, 0, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 1, 1, 1],

                ],
                'start': (1, 1),
                'goal': (7, 1),
}

MAZES = [MAZE_1, MAZE_2, MAZE_3]

# Helpers

def get_random_maze():
	return random.choice(MAZES)

# This method helps mazeDrawer.py and Navigator.py by coverting the 2D list into turtlesim world

def grid_to_world(row, col, center=True):
	# Convert grid to turtlesim world
	# Flip coordinates to match turtlesim

	x = ORIGIN_X + col * CELL_SIZE
	# Flip the y, as turtlesim y=0 is at bottom
	y = ORIGIN_Y + (GRID_ROWS - 1 - row) * CELL_SIZE
	if center:
		x += CELL_SIZE / 2.0
		y += CELL_SIZE / 2.0
	return x,y

# Needed by Navigator.py to convert turtle position back to grid world to make decisions

def world_to_grid(x, y):
	# Convert turtlesim world back to grid, good for navigator
	col = int((x- ORIGIN_X) / CELL_SIZE)
	row = int(GRID_ROWS - 1 - (y - ORIGIN_Y) / CELL_SIZE)

	# Clamp values to avoid errors
	row = max(0, min(GRID_ROWS - 1, row))
	col = max(0, min(GRID_COLS - 1, col))
	return row, col

def is_wall(grid, row, col):
	# Return true if out of bounds
	if row < 0 or row >= GRID_ROWS or col < 0 or col >= GRID_COLS:
		return True
	# Return true/false based on if wall (1)
	return grid[row][col] == 1

def get_neighbours(grid, row, col):
	# Return a list of open spaces, in order up down left right
	candidates = [
		(row - 1, col),
		(row + 1, col),
		(row, col - 1),
		(row, col+ 1),
	]
	# Loop through candidates (r,c), returns valid ones (not a wall)
	return [(r, c) for r, c in candidates if not is_wall(grid, r, c)]
