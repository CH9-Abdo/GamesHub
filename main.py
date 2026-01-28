import pygame
import sys
from settings import *
from managers.state_manager import GameStateManager
from ui.menu import MainMenu
from games.snake import SnakeGame
from games.tetris import TetrisGame
from games.breakout import BreakoutGame

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Define a callback to return to the menu
    def return_to_menu():
        state_manager.set_state(menu)

    # Initialize Games
    snake_game = SnakeGame(screen, return_to_menu)
    tetris_game = TetrisGame(screen, return_to_menu)
    breakout_game = BreakoutGame(screen, return_to_menu)

    # Dictionary of games for the menu
    games_dict = {
        "Tetris": tetris_game,
        "Snake": snake_game,
        "Breakout": breakout_game
    }

    # Initialize State Manager (start with temporary state until menu is ready, or just pass None)
    # Actually, we can create the menu now.
    state_manager = GameStateManager(None)
    
    menu = MainMenu(screen, state_manager, games_dict)
    
    # Set initial state to Menu
    state_manager.set_state(menu)

    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Pass event to current state
            state_manager.handle_events(event)

        # Update
        state_manager.update()

        # Draw
        state_manager.draw()
        
        # Render
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
