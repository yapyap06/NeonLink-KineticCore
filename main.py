import pygame
import sys
import cv2
import numpy as np
from src.tetris_core import TetrisEngine, GRID_WIDTH, GRID_HEIGHT, Piece
from src.ai.hand_tracker import HandTracker

# Window configurations
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
PLAY_WIDTH = GRID_WIDTH * BLOCK_SIZE
PLAY_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

# These will be dynamically calculated based on screen resolution
TOP_LEFT_X = 50 
TOP_LEFT_Y = 50
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
GRID_COLOR = (40, 40, 40)

# Font Name: Use a monospaced "cyber" feeling font if available, fallback to courier
FONT_NAME = 'couriernew'

def draw_grid(surface):
    for i in range(GRID_HEIGHT):
        pygame.draw.line(surface, GRID_COLOR, (TOP_LEFT_X, TOP_LEFT_Y + i * BLOCK_SIZE),
                         (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i * BLOCK_SIZE))
        for j in range(GRID_WIDTH):
            pygame.draw.line(surface, GRID_COLOR, (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y),
                             (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))

def draw_window(surface, engine, vibe_score, high_score):
    surface.fill(BLACK)
    
    # Title (Moved higher and centered over the whole window)
    font = pygame.font.SysFont(FONT_NAME, 50, bold=True)
    label = font.render('NEONLINK: KINETIC CORE', 1, (0, 255, 255))
    surface.blit(label, (WINDOW_WIDTH / 2 - (label.get_width() / 2), 15))

    # Scores (Moved slightly lower)
    score_font = pygame.font.SysFont(FONT_NAME, 25, bold=True)
    score_lbl = score_font.render(f'SCORE: {engine.score}', 1, WHITE)
    hs_lbl = score_font.render(f'HIGH: {high_score}', 1, WHITE)
    
    # Moved to the right side of the board for better spacing
    info_x = TOP_LEFT_X + PLAY_WIDTH + 80
    surface.blit(score_lbl, (info_x, TOP_LEFT_Y))
    surface.blit(hs_lbl, (info_x, TOP_LEFT_Y + 40))

    # Grid pieces
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            if engine.grid[i][j] != (0, 0, 0):
                pygame.draw.rect(surface, engine.grid[i][j], (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    # Current Piece
    if engine.current_piece:
        shape_pos = engine.convert_shape_format(engine.current_piece)
        for i, pos in enumerate(shape_pos):
            x, y = pos
            if y > -1:
                pygame.draw.rect(surface, engine.current_piece.color, (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    # Grid lines
    draw_grid(surface)
    pygame.draw.rect(surface, (0, 255, 255), (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 5)
    
    # Draw Vibe Meter - Scaled by frequency, but clamped to 100 max
    vibe_bar_rect = pygame.Rect(info_x, TOP_LEFT_Y + 120, 40, PLAY_HEIGHT - 120)
    pygame.draw.rect(surface, GRAY, vibe_bar_rect)
    
    # Render Vibe Level
    v_score_clamped = max(0.0, min(100.0, vibe_score))
    fill_h = int((v_score_clamped / 100.0) * vibe_bar_rect.height)
    
    # Make color glow more intense as vibe increases
    vibe_color = (int(255 * (v_score_clamped/100)), 0, 255)
    pygame.draw.rect(surface, vibe_color, (vibe_bar_rect.x, vibe_bar_rect.y + vibe_bar_rect.height - fill_h, vibe_bar_rect.width, fill_h))
    
    vibe_font = pygame.font.SysFont(FONT_NAME, 25, bold=True)
    vibe_lbl = vibe_font.render('VIBE', 1, (255, 0, 255))
    surface.blit(vibe_lbl, (vibe_bar_rect.x - 10, vibe_bar_rect.y - 30))
    
    # Legend panel
    legend_font = pygame.font.SysFont(FONT_NAME, 20)
    legend_x = TOP_LEFT_X + 20
    legend_y = TOP_LEFT_Y + PLAY_HEIGHT + 20
    controls_text = [
        "CONTROLS",
        "Arrows / W : Move & Rotate",
        "P          : Pause",
        "ESC        : Quit",
        "AI OPEN    : Slow Time",
        "AI FIST    : Kinetic Slam"
    ]
    for idx, line in enumerate(controls_text):
        lbl = legend_font.render(line, 1, WHITE if idx > 0 else (0, 255, 255))
        surface.blit(lbl, (legend_x, legend_y + (idx * 25)))
        
def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT, TOP_LEFT_X, TOP_LEFT_Y
    
    pygame.init()
    pygame.font.init()
    pygame.mixer.init() # Init audio
    
    # Load sounds
    try:
        clear_sound = pygame.mixer.Sound('assets/clear.wav')
        drop_sound = pygame.mixer.Sound('assets/drop.wav')
        bomb_sound = pygame.mixer.Sound('assets/bomb.wav')
        pygame.mixer.music.load('assets/bgm.wav')
        pygame.mixer.music.set_volume(0.5)
        if drop_sound: drop_sound.set_volume(0.5)
        if bomb_sound: bomb_sound.set_volume(0.8)
        # Start BGM loop
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("Audio load error:", e)
        clear_sound = None
        drop_sound = None
        bomb_sound = None
        
    # Set to Fullscreen
    infoObject = pygame.display.Info()
    WINDOW_WIDTH = infoObject.current_w
    WINDOW_HEIGHT = infoObject.current_h
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption('NeonLink: Kinetic Core')
    
    # Dynamically center the play area
    TOP_LEFT_X = (WINDOW_WIDTH - PLAY_WIDTH) // 2
    TOP_LEFT_Y = WINDOW_HEIGHT - PLAY_HEIGHT - 50
    
    engine = TetrisEngine()
    clock = pygame.time.Clock()
    
    # Load High Score
    try:
        with open('assets/highscore.txt', 'r') as f:
            high_score = int(f.read())
    except:
        high_score = 0
        
    # Base mechanics
    fall_time = 0
    base_fall_speed = 0.5  # time in seconds
    vibe_score = 0.0
    
    # Initialize Camera
    tracker = HandTracker()
    print("Starting AI Camera...")
    tracker.start()
    
    # Slam debounce tracking
    fist_released = True
    
    is_paused = False
    
    run = True
    while run:
        player_interacted = False
        
        # 1. Update Fall Speed based on AI
        frame, gesture = tracker.get_data()
        
        # Handle Input Events first to catch Quit and Pause immediately
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                elif event.key == pygame.K_p:
                    is_paused = not is_paused
                # Allow restart via R key when game over
                elif engine.game_over and event.key == pygame.K_r:
                    engine = TetrisEngine()
                    fall_time = 0
                    vibe_score = 0.0
                    fist_released = True
                    # Re-start BGM
                    pygame.mixer.music.play(-1)
                
                # Gameplay controls
                elif not engine.game_over and not is_paused:
                    player_interacted = True
                    if event.key == pygame.K_LEFT:
                        engine.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        engine.move_piece(1, 0)
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        engine.rotate_piece()
                    elif event.key == pygame.K_DOWN:
                        # Keyboard soft drop
                        if drop_sound: drop_sound.play()
                        lines_cleared = engine.move_piece(0, 1)
                        if lines_cleared > 0 and clear_sound:
                            clear_sound.play()
                            
        if is_paused:
            # Render pause screen over current state
            draw_window(win, engine, vibe_score, high_score)
            
            pause_font = pygame.font.SysFont(FONT_NAME, 80, bold=True)
            pause_lbl = pause_font.render('PAUSED', 1, WHITE)
            win.blit(pause_lbl, (WINDOW_WIDTH / 2 - pause_lbl.get_width() / 2, WINDOW_HEIGHT / 2 - 50))
            
            pygame.display.update()
            clock.tick()
            continue
            
        current_fall_speed = base_fall_speed
        
        # Update fist release state
        if gesture != "CLOSED_FIST":
            fist_released = True
            
        # Handle Game Over State
        if engine.game_over:
            # Check for restart inputs
            restart = False
            if gesture == "THUMB_UP":
                restart = True
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    run = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    restart = True
                    
            if restart:
                # Reset engine
                engine = TetrisEngine()
                fall_time = 0
                vibe_score = 0.0
                fist_released = True
            else:
                # Render Game Over Screen
                draw_window(win, engine, vibe_score, high_score)
                font_go = pygame.font.SysFont('comicsans', 80)
                go_label = font_go.render('GAME OVER', 1, (255, 0, 0))
                win.blit(go_label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (go_label.get_width() / 2), WINDOW_HEIGHT / 2 - 50))
                
                font_rst = pygame.font.SysFont('comicsans', 40)
                rst_label = font_rst.render('Press R or Thumb Up to Restart', 1, WHITE)
                win.blit(rst_label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (rst_label.get_width() / 2), WINDOW_HEIGHT / 2 + 50))
                
                pygame.display.update()
                clock.tick()
                continue
        
        # Phase 2 Gesture mapping
        if gesture == "OPEN_PALM":
            current_fall_speed *= 2.0  # Slow-motion
        elif gesture == "CLOSED_FIST" and fist_released:
            # Trigger Hard Drop (Kinetic Slam)
            if drop_sound: drop_sound.play()
            lines_cleared = engine.hard_drop()
            if lines_cleared > 0 and clear_sound:
                clear_sound.play()
            
            fist_released = False
            # Reset fall time to avoid double dropping immediately after spawn
            fall_time = 0
            
        # 2. Handle Tetris Falling
        fall_time += clock.get_rawtime()
        clock.tick()
        
        if fall_time / 1000 >= current_fall_speed:
            fall_time = 0
            if not engine.game_over:
                engine.current_piece.y += 1
                if drop_sound: drop_sound.play()
                
                if not engine.valid_space(engine.current_piece) and engine.current_piece.y > 0:
                    engine.current_piece.y -= 1
                    lines_cleared = engine.lock_piece()
                    if lines_cleared > 0 and clear_sound:
                        clear_sound.play()
                        
        # Update Vibe Score
        if player_interacted and gesture != "NONE":
            vibe_score = min(vibe_score + 5.0, 100.0)
        else:
            vibe_score = max(vibe_score - 0.2, 0.0)

        # 4. Render
        draw_window(win, engine, vibe_score, high_score)
        
        # Display Ghost Window (Moved higher so it doesn't overlap text)
        ghost_w, ghost_h = 240, 180
        if frame is not None:
            # OpenCV to Pygame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pyg = pygame.surfarray.make_surface(np.swapaxes(frame_rgb, 0, 1))
            
            # Scale down
            frame_pyg = pygame.transform.scale(frame_pyg, (ghost_w, ghost_h))
            
            # Draw with neon border - align to Top Right
            gw_x = WINDOW_WIDTH - ghost_w - 20
            gw_y = 60
            pygame.draw.rect(win, (255, 0, 255), (gw_x - 2, gw_y - 2, ghost_w + 4, ghost_h + 4), 2)
            win.blit(frame_pyg, (gw_x, gw_y))
        
        # Display Gesture Info - positioned right under Ghost Camera
        gesture_font = pygame.font.SysFont(FONT_NAME, 25, bold=True)
        gesture_lbl = gesture_font.render(f'AI: {gesture}', 1, (0, 255, 0) if gesture != "NONE" else WHITE)
        win.blit(gesture_lbl, (WINDOW_WIDTH - ghost_w - 20, 250))
        
        # End Game Label (Handle high score save on death trigger)
        if getattr(engine, 'just_died', False) == False and engine.game_over:
            engine.just_died = True
            
            # Play explosion, stop BGM
            pygame.mixer.music.stop()
            if bomb_sound:
                bomb_sound.play()
                
            # Save high score
            if engine.score > high_score:
                high_score = engine.score
                with open('assets/highscore.txt', 'w') as f:
                    f.write(str(engine.score))
            
        pygame.display.update()

    tracker.stop()
    pygame.quit()

if __name__ == '__main__':
    main()
