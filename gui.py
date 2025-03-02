from tkinter import *
import numpy as np

class GUI:
    def __init__(self, controller):
        self._controller = controller
        self._grid = self._controller._grid
        self._screen = Tk()
        self._screen.title("HexWar")
        self._grid_canvas = Canvas(self._screen, width=int(np.sqrt(3) * 20 * self._grid.get_size()*1.6), height=int(2 * 20 * self._grid.get_size()*0.9))
        self._grid_canvas.pack()
        self.stop = False
        self.launch = False
        self._draw()

    def run(self):
        while not self.stop:
            if self.launch:
                self._controller.update()
                self._draw()
                self._screen.update()
                self.check_win()
            else:
                self._screen.update()

    def check_win(self):
        if self._controller._winner != 0:
            self.launch = False
            self._show_winner()

    def _draw(self):
        self._grid_canvas.delete("all")
        size_hex = 20
        w = np.sqrt(3) * size_hex
        h = 2 * size_hex
        for y in range(self._grid.get_size()):
            for x in range(self._grid.get_size()):
                pos_x = w/2 + (y*w/2) + x*w
                pos_y = w + (h*3/4)*y
                color = 'grey'
                player = self._grid.get_hex([x, y])
                if player == 1:
                    color = 'red'
                elif player == 2:
                    color = 'blue'
                self._draw_hex([pos_x, pos_y], color)

    def _draw_hex(self, coordinates, color='gray'):
        size = 20
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = np.pi / 180 * angle_deg
            points.append([coordinates[0] + size * np.cos(angle_rad), coordinates[1] + size * np.sin(angle_rad)])
        self._grid_canvas.create_polygon(points, outline='white', fill=color, width=2)

    def _show_winner(self):
        winner = self._controller._winner
        player_name = self._controller._player1.name if winner == 1 else self._controller._player2.name
        Label(self._screen, text=f"{player_name} wins!").pack()

    def start(self):
        self.launch = True

    def stop(self):
        self.launch = False
