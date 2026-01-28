class GameStateManager:
    def __init__(self, initial_state):
        self.current_state = initial_state

    def get_state(self):
        return self.current_state

    def set_state(self, state):
        self.current_state = state
        if hasattr(self.current_state, 'reset'):
            self.current_state.reset()
        # If the state has an 'active' flag, set it
        if hasattr(self.current_state, 'active'):
            self.current_state.active = True

    def handle_events(self, event):
        self.current_state.handle_events(event)

    def update(self):
        self.current_state.update()

    def draw(self):
        self.current_state.draw()
