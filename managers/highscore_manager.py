import json
import os

HIGHSCORE_FILE = "highscores.json"

class HighscoreManager:
    def __init__(self):
        self.scores = {}
        self._load_scores()

    def _load_scores(self):
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, 'r') as f:
                    self.scores = json.load(f)
            except (json.JSONDecodeError, IOError):
                print("Failed to load high scores. Starting fresh.")
                self.scores = {}
        else:
            self.scores = {}

    def get_score(self, game_name):
        return self.scores.get(game_name, 0)

    def save_score(self, game_name, new_score):
        """
        Updates the high score for a game if the new score is higher.
        Returns True if a new high score was set, False otherwise.
        """
        current_high = self.get_score(game_name)
        if new_score > current_high:
            self.scores[game_name] = new_score
            self._write_to_file()
            return True
        return False

    def _write_to_file(self):
        try:
            with open(HIGHSCORE_FILE, 'w') as f:
                json.dump(self.scores, f, indent=4)
        except IOError as e:
            print(f"Failed to save high scores: {e}")