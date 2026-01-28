import pygame
from abc import ABC, abstractmethod

class BaseGame(ABC):
    def __init__(self, screen, create_game_callback=None, game_over_callback=None):
        self.screen = screen
        # Callback to return to menu or switch states
        self.create_game_callback = create_game_callback 
        self.game_over_callback = game_over_callback
        self.active = False

    @abstractmethod
    def handle_events(self, event):
        """Process input events."""
        pass

    @abstractmethod
    def update(self):
        """Update game logic."""
        pass

    @abstractmethod
    def draw(self):
        """Render the game to the screen."""
        pass

    def reset(self):
        """Reset the game state to start over."""
        pass
