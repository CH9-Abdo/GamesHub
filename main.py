import pygame
import sys
from settings import *
from managers.state_manager import GameStateManager
from managers.highscore_manager import HighscoreManager
from managers.sound_manager import SoundManager
from ui.menu import MainMenu
from games.snake import SnakeGame
from games.tetris import TetrisGame
from games.breakout import BreakoutGame
from games.pong import PongGame
from games.invaders import InvadersGame
from games.flappy import FlappyGame

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Initialize Managers first (required for callbacks)
    highscore_manager = HighscoreManager()
    sound_manager = SoundManager()
    sound_manager.play_music()
    
    # Initialize State Manager before games (games need access to it via callback)
    state_manager = GameStateManager(None)
    
    # Initialize Menu (needed for return_to_menu callback)
    # Games dict will be populated after games are created
    menu = MainMenu(screen, state_manager, {})
    
    # Define callback to return to menu AFTER menu is created
    # This prevents the callback from referencing undefined objects
    def return_to_menu():
        state_manager.set_state(menu)
    
    # Now initialize games with the valid callback
    snake_game = SnakeGame(screen, return_to_menu, highscore_manager, sound_manager, "Snake")
    tetris_game = TetrisGame(screen, return_to_menu, highscore_manager, sound_manager, "Tetris")
    breakout_game = BreakoutGame(screen, return_to_menu, highscore_manager, sound_manager, "Breakout")
    pong_game = PongGame(screen, return_to_menu, highscore_manager, sound_manager, "Pong")
    invaders_game = InvadersGame(screen, return_to_menu, highscore_manager, sound_manager, "Invaders")
    flappy_game = FlappyGame(screen, return_to_menu, highscore_manager, sound_manager, "Flappy")

    # Dictionary of games for the menu
    games_dict = {
        "Tetris": tetris_game,
        "Snake": snake_game,
        "Breakout": breakout_game,
        "Pong": pong_game,
        "Invaders": invaders_game,
        "Flappy": flappy_game
    }
    
    # Update menu with games dictionary
    menu.games = games_dict
    menu.game_names = list(menu.games.keys()) + ["Quit"]
    
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