import pygame
import os

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.sound_dir = "assets/sounds"
        self._load_sounds()

    def _load_sounds(self):
        if not os.path.exists(self.sound_dir):
            print("Sound directory not found. Skipping audio.")
            return

        sound_files = {
            "select": "select.wav",
            "shoot": "shoot.wav",
            "jump": "jump.wav",
            "explosion": "explosion.wav",
            "gameover": "gameover.wav",
            "score": "score.wav"
        }

        for name, filename in sound_files.items():
            path = os.path.join(self.sound_dir, filename)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(0.3)
                except Exception as e:
                    print(f"Failed to load sound {filename}: {e}")
            else:
                print(f"Sound file missing: {filename}")

    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def play_music(self):
        music_path = os.path.join(self.sound_dir, "music.wav")
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1) # Loop indefinitely
            except Exception as e:
                print(f"Failed to load music: {e}")
        else:
            print("Music file not found.")

    def stop_music(self):
        pygame.mixer.music.stop()
