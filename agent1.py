import numpy as np
from agent import Agent

class CustomPlayer(Agent):
    def __init__(self, size, player_number, adv_number):
        super().__init__(size, player_number, adv_number)
        self.name = "Random"
        self._possible_moves = [[x, y] for x in range(self.size) for y in range(self.size)]

    def step(self):
        move = self._possible_moves.pop(np.random.randint(len(self._possible_moves)))
        self.set_hex(self.player_number, move)
        return move

    def update(self, move_other_player):
        self.set_hex(self.adv_number, move_other_player)
        if move_other_player in self._possible_moves:
            self._possible_moves.remove(move_other_player)