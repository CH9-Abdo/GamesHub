# How to Integrate Custom Assets

This project uses procedural drawing (rectangles, circles) for simplicity and performance. However, integrating images and sounds is straightforward thanks to the modular `BaseGame` structure.

## Adding Images (Sprites)

1.  **Load the Image**: In your game class's `__init__` method, load the image.
    ```python
    self.player_image = pygame.image.load("assets/images/player.png").convert_alpha()
    ```
2.  **Draw the Image**: In the `draw()` method, replace `pygame.draw.rect(...)` with `blit`.
    ```python
    # Old: pygame.draw.rect(self.screen, color, rect)
    # New:
    self.screen.blit(self.player_image, rect)
    ```

## Adding Sounds

1.  **Initialize Mixer**: Ensure `pygame.mixer.init()` is called in `main.py` (it's usually handled by `pygame.init()`).
2.  **Load the Sound**:
    ```python
    self.jump_sound = pygame.mixer.Sound("assets/sounds/jump.wav")
    ```
3.  **Play the Sound**: Trigger it in your logic (e.g., inside `handle_events` or `update`).
    ```python
    if jumped:
        self.jump_sound.play()
    ```

## Organization
Create an `assets/` folder in the root directory:
```
GamesHub/
├── assets/
│   ├── images/
│   └── sounds/
├── main.py
...
```
