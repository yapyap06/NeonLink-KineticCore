import pygame
import random

# Standard Tetris grid dimensions
GRID_WIDTH = 10
GRID_HEIGHT = 20

# Tetromino Shapes
SHAPES = [
    [['.....',
      '..#..',
      '..#..',
      '..#..',
      '..#..',
      '.....'],
     ['.....',
      '.....',
      '####.',
      '.....',
      '.....',
      '.....']], # I
     
    [['.....',
      '.....',
      '..##.',
      '..##.',
      '.....',
      '.....']], # O

    [['.....',
      '.....',
      '..#..',
      '.###.',
      '.....',
      '.....'],
     ['.....',
      '..#..',
      '..##.',
      '..#..',
      '.....',
      '.....'],
     ['.....',
      '.....',
      '.###.',
      '..#..',
      '.....',
      '.....'],
     ['.....',
      '..#..',
      '.##..',
      '..#..',
      '.....',
      '.....']], # T
      
    [['.....',
      '.....',
      '.##..',
      '..##.',
      '.....',
      '.....'],
     ['.....',
      '..#..',
      '.##..',
      '.#...',
      '.....',
      '.....']], # S

    [['.....',
      '.....',
      '..##.',
      '.##..',
      '.....',
      '.....'],
     ['.....',
      '.#...',
      '.##..',
      '..#..',
      '.....',
      '.....']], # Z

    [['.....',
      '.....',
      '.###.',
      '.#...',
      '.....',
      '.....'],
     ['.....',
      '.##..',
      '..#..',
      '..#..',
      '.....',
      '.....'],
     ['.....',
      '...#.',
      '.###.',
      '.....',
      '.....',
      '.....'],
     ['.....',
      '..#..',
      '..#..',
      '...##',
      '.....',
      '.....']], # J

    [['.....',
      '.....',
      '.###.',
      '...#.',
      '.....',
      '.....'],
     ['.....',
      '..#..',
      '..#..',
      '.##..',
      '.....',
      '.....'],
     ['.....',
      '.#...',
      '.###.',
      '.....',
      '.....',
      '.....'],
     ['.....',
      '...##',
      '..#..',
      '..#..',
      '.....',
      '.....']]  # L
]

# Shape colors (R, G, B) for Neon Vibe
COLORS = [
    (0, 255, 255),  # Cyan - I
    (255, 255, 0),  # Yellow - O
    (255, 0, 255),  # Purple - T
    (0, 255, 0),    # Green - S
    (255, 0, 0),    # Red - Z
    (0, 0, 255),    # Blue - J
    (255, 165, 0)   # Orange - L
]

class Piece:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.shape_type = random.randint(0, len(SHAPES) - 1)
        self.rotation = 0
        self.color = COLORS[self.shape_type]

    def image(self):
        return SHAPES[self.shape_type][self.rotation]

class TetrisEngine:
    def __init__(self):
        self.grid = self.create_grid()
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.score = 0
        self.game_over = False

    def create_grid(self):
        return [[(0, 0, 0) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def get_new_piece(self):
        return Piece(GRID_WIDTH // 2 - 2, 0)

    def convert_shape_format(self, piece):
        positions = []
        format = piece.image()
        
        for i, line in enumerate(format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '#':
                    positions.append((piece.x + j, piece.y + i))
                    
        # Offset to center the shape
        for i, pos in enumerate(positions):
            positions[i] = (pos[0] - 2, pos[1] - 4)
            
        return positions

    def valid_space(self, piece):
        accepted_pos = [[(j, i) for j in range(GRID_WIDTH) if self.grid[i][j] == (0, 0, 0)] for i in range(GRID_HEIGHT)]
        accepted_pos = [j for sub in accepted_pos for j in sub]
        
        formatted = self.convert_shape_format(piece)
        
        for pos in formatted:
            if pos not in accepted_pos:
                if pos[1] > -1:
                    return False
        return True

    def check_lost(self):
        # A player loses if any locked blocks reach the very top of the grid (y=0)
        # We check the top row of the grid to ensure we only end the game when the stack fills up
        for pos in self.grid[0]:
            if pos != (0, 0, 0):
                return True
        return False

    def lock_piece(self):
        form = self.convert_shape_format(self.current_piece)
        for pos in form:
            x, y = pos
            if y > -1:
                self.grid[y][x] = self.current_piece.color
                
        self.current_piece = self.next_piece
        self.next_piece = self.get_new_piece()
        cleared_lines = self.clear_rows()
        
        if self.check_lost():
            self.game_over = True
            
        return cleared_lines

    def clear_rows(self):
        inc = 0
        # Iterate backwards from bottom to top
        for i in range(len(self.grid) - 1, -1, -1):
            row = self.grid[i]
            # If there are no empty blocks in this row, it's full
            if (0, 0, 0) not in row:
                inc += 1
                ind = i
                
                # Clear the row
                for j in range(len(row)):
                    self.grid[i][j] = (0, 0, 0)
                    
        if inc > 0:
            # We found full rows. Now shift everything above `ind` downwards by `inc` rows
            # We iterate backwards starting just above the highest cleared line
            for i in range(ind - 1, -1, -1):
                for j in range(len(self.grid[i])):
                    if self.grid[i][j] != (0, 0, 0):
                        # Move the block down
                        self.grid[i + inc][j] = self.grid[i][j]
                        # Empty the old spot
                        self.grid[i][j] = (0, 0, 0)
                        
            self.score += inc * 100
            
        return inc

    def move_piece(self, dx, dy):
        cleared = 0
        if not self.game_over:
            self.current_piece.x += dx
            self.current_piece.y += dy
            if not self.valid_space(self.current_piece):
                self.current_piece.x -= dx
                self.current_piece.y -= dy
                # If moving down failed, lock it
                if dy > 0:
                    cleared = self.lock_piece()
        return cleared

    def rotate_piece(self):
        if not self.game_over:
            self.current_piece.rotation = (self.current_piece.rotation + 1) % len(SHAPES[self.current_piece.shape_type])
            if not self.valid_space(self.current_piece):
                # Revert
                self.current_piece.rotation = (self.current_piece.rotation - 1) % len(SHAPES[self.current_piece.shape_type])

    def hard_drop(self):
        """Immediately drops the piece to the lowest valid position and locks it."""
        cleared = 0
        if not self.game_over:
            while self.valid_space(self.current_piece):
                self.current_piece.y += 1
            # Back up one space since the last increment made it invalid
            self.current_piece.y -= 1
            # Lock the piece
            cleared = self.lock_piece()
        return cleared
