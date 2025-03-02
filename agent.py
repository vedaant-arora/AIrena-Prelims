class Agent:
    def __init__(self, size, player_number, adv_number):
        self.size = size
        self.player_number = player_number
        self.adv_number = adv_number
        self.name = "Base Agent"

    def step(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def update(self, move_other_player):
        raise NotImplementedError("Subclass must implement abstract method")
