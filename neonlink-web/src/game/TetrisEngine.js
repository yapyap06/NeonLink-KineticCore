// Standard Tetris grid dimensions
export const GRID_WIDTH = 10;
export const GRID_HEIGHT = 20;

// Neon Vibe Colors corresponding to standard pieces
export const COLORS = [
    '#00FFFF', // Cyan - I
    '#FFFF00', // Yellow - O
    '#FF00FF', // Purple - T
    '#00FF00', // Green - S
    '#FF0000', // Red - Z
    '#0000FF', // Blue - J
    '#FFA500', // Orange - L
];

const SHAPES = [
    // I (Cyan)
    [
        ['.....', '..#..', '..#..', '..#..', '..#..', '.....'],
        ['.....', '.....', '####.', '.....', '.....', '.....']
    ],
    // O (Yellow)
    [
        ['.....', '.....', '..##.', '..##.', '.....', '.....']
    ],
    // T (Purple)
    [
        ['.....', '.....', '..#..', '.###.', '.....', '.....'],
        ['.....', '..#..', '..##.', '..#..', '.....', '.....'],
        ['.....', '.....', '.###.', '..#..', '.....', '.....'],
        ['.....', '..#..', '.##..', '..#..', '.....', '.....']
    ],
    // S (Green)
    [
        ['.....', '.....', '.##..', '..##.', '.....', '.....'],
        ['.....', '..#..', '.##..', '.#...', '.....', '.....']
    ],
    // Z (Red)
    [
        ['.....', '.....', '..##.', '.##..', '.....', '.....'],
        ['.....', '.#...', '.##..', '..#..', '.....', '.....']
    ],
    // J (Blue)
    [
        ['.....', '.....', '.###.', '.#...', '.....', '.....'],
        ['.....', '.##..', '..#..', '..#..', '.....', '.....'],
        ['.....', '...#.', '.###.', '.....', '.....', '.....'],
        ['.....', '..#..', '..#..', '...##', '.....', '.....']
    ],
    // L (Orange)
    [
        ['.....', '.....', '.###.', '...#.', '.....', '.....'],
        ['.....', '..#..', '..#..', '.##..', '.....', '.....'],
        ['.....', '.#...', '.###.', '.....', '.....', '.....'],
        ['.....', '...##', '..#..', '..#..', '.....', '.....']
    ]
];

class Piece {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this.shape_type = Math.floor(Math.random() * SHAPES.length);
        this.rotation = 0;
        this.color = COLORS[this.shape_type];
    }

    image() {
        return SHAPES[this.shape_type][this.rotation];
    }
}

export class TetrisEngine {
    constructor() {
        this.grid = this.createGrid();
        this.currentPiece = this.getNewPiece();
        this.nextPiece = this.getNewPiece();
        this.score = 0;
        this.gameOver = false;
    }

    createGrid() {
        const grid = [];
        for (let i = 0; i < GRID_HEIGHT; i++) {
            const row = [];
            for (let j = 0; j < GRID_WIDTH; j++) {
                row.push(null); // null means empty (instead of Python's (0,0,0))
            }
            grid.push(row);
        }
        return grid;
    }

    getNewPiece() {
        return new Piece(Math.floor(GRID_WIDTH / 2) - 2, 0);
    }

    convertShapeFormat(piece) {
        const positions = [];
        const format = piece.image();

        for (let i = 0; i < format.length; i++) {
            const line = format[i];
            for (let j = 0; j < line.length; j++) {
                if (line[j] === '#') {
                    positions.push({ x: piece.x + j, y: piece.y + i });
                }
            }
        }

        // Offset to center the shape (same math as Python core)
        for (let i = 0; i < positions.length; i++) {
            positions[i].x -= 2;
            positions[i].y -= 4;
        }

        return positions;
    }

    validSpace(piece) {
        // Array of all valid empty positions
        const acceptedPos = [];
        for (let i = 0; i < GRID_HEIGHT; i++) {
            for (let j = 0; j < GRID_WIDTH; j++) {
                if (this.grid[i][j] === null) {
                    acceptedPos.push({ x: j, y: i });
                }
            }
        }

        const formatted = this.convertShapeFormat(piece);
        for (let i = 0; i < formatted.length; i++) {
            const pos = formatted[i];
            // Check if pos exists in acceptedPos
            const isAccepted = acceptedPos.some((acc) => acc.x === pos.x && acc.y === pos.y);
            if (!isAccepted) {
                if (pos.y > -1) {
                    return false;
                }
            }
        }
        return true;
    }

    checkLost() {
        for (let j = 0; j < GRID_WIDTH; j++) {
            if (this.grid[0][j] !== null) {
                return true;
            }
        }
        return false;
    }

    lockPiece() {
        const form = this.convertShapeFormat(this.currentPiece);
        for (let i = 0; i < form.length; i++) {
            const { x, y } = form[i];
            if (y > -1) {
                this.grid[y][x] = this.currentPiece.color;
            }
        }

        this.currentPiece = this.nextPiece;
        this.nextPiece = this.getNewPiece();
        const clearedLines = this.clearRows();

        if (this.checkLost()) {
            this.gameOver = true;
        }
        return clearedLines;
    }

    clearRows() {
        let inc = 0;
        // Iterate backwards from bottom to top
        for (let i = GRID_HEIGHT - 1; i >= 0; i--) {
            const row = this.grid[i];
            // If there are no 'null' blocks, the row is full
            if (!row.includes(null)) {
                inc += 1;
                const ind = i;

                // Clear the row
                for (let j = 0; j < GRID_WIDTH; j++) {
                    this.grid[i][j] = null;
                }

                // Shift everything above `ind` downwards
                for (let k = ind - 1; k >= 0; k--) {
                    for (let j = 0; j < GRID_WIDTH; j++) {
                        if (this.grid[k][j] !== null) {
                            this.grid[k + 1][j] = this.grid[k][j];
                            this.grid[k][j] = null;
                        }
                    }
                }

                // Since we shifted everything down by 1, we must re-check this same physical line index
                // because the row that just fell into this index might ALSO be full.
                i++;
            }
        }

        if (inc > 0) {
            this.score += inc * 100;
        }
        return inc;
    }

    movePiece(dx, dy) {
        let cleared = 0;
        if (!this.gameOver) {
            this.currentPiece.x += dx;
            this.currentPiece.y += dy;
            if (!this.validSpace(this.currentPiece)) {
                this.currentPiece.x -= dx;
                this.currentPiece.y -= dy;
                // Lock it if moving down failed
                if (dy > 0) {
                    cleared = this.lockPiece();
                }
            }
        }
        return cleared;
    }

    rotatePiece() {
        if (!this.gameOver) {
            this.currentPiece.rotation =
                (this.currentPiece.rotation + 1) % SHAPES[this.currentPiece.shape_type].length;
            if (!this.validSpace(this.currentPiece)) {
                // Revert
                this.currentPiece.rotation =
                    (this.currentPiece.rotation - 1 + SHAPES[this.currentPiece.shape_type].length) %
                    SHAPES[this.currentPiece.shape_type].length;
            }
        }
    }

    hardDrop() {
        let cleared = 0;
        if (!this.gameOver) {
            while (this.validSpace(this.currentPiece)) {
                this.currentPiece.y += 1;
            }
            this.currentPiece.y -= 1;
            cleared = this.lockPiece();
        }
        return cleared;
    }
}
