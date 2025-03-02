import tkinter as tk
import numpy as np

class GUI:
    def __init__(self, controller):
        self._controller = controller
        self._grid = self._controller._grid
        self._screen = tk.Tk()
        self._screen.title("HexWar")
        self._screen.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._screen.configure(bg='#f0f0f0')

        self._grid_canvas = tk.Canvas(self._screen, width=int(np.sqrt(3) * 20 * self._grid.get_size()*1.6),
                                      height=int(2 * 20 * self._grid.get_size()*0.9), bg='white', bd=2, relief='raised')
        self._grid_canvas.pack(padx=10, pady=10)
        
        self._info_frame = tk.Frame(self._screen, bg='#f0f0f0')
        self._info_frame.pack(pady=10)
        
        tk.Label(self._info_frame, text="Player 1 (Red)", fg='red', bg='#f0f0f0', font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        tk.Label(self._info_frame, text="Player 2 (Blue)", fg='blue', bg='#f0f0f0', font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        
        self._start_button = tk.Button(self._screen, text="Start Game", command=self.start, bg='#4CAF50', fg='white', font=('Arial', 12))
        self._start_button.pack(pady=10)
        
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
                color = 'lightgray'
                player = self._grid.get_hex([x, y])
                if player == 1:
                    color = 'red'
                elif player == 2:
                    color = 'blue'
                self._draw_hex([pos_x, pos_y], color)

    def _draw_hex(self, coordinates, color='lightgray'):
        size = 20
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = np.pi / 180 * angle_deg
            points.append([coordinates[0] + size * np.cos(angle_rad), coordinates[1] + size * np.sin(angle_rad)])
        self._grid_canvas.create_polygon(points, outline='black', fill=color, width=2)

    def _show_winner(self):
        winner = self._controller._winner
        player_name = self._controller._player1.name if winner == 1 else self._controller._player2.name
        color = 'red' if winner == 1 else 'blue'
        winner_label = tk.Label(self._screen, text=f"{player_name} (Player {winner}) wins!", fg=color, bg='#f0f0f0', font=('Arial', 14, 'bold'))
        winner_label.pack(pady=10)
        self._start_button.config(text="Play Again", command=self.reset_game)

    def reset_game(self):
        self._controller._grid = self._controller._grid.__class__(self._controller._grid.get_size())
        self._controller._winner = 0
        self._controller._current_player = 1
        self._draw()
        self.launch = False
        self._start_button.config(text="Start Game", command=self.start)
        for widget in self._screen.winfo_children():
            if isinstance(widget, tk.Label) and "wins" in widget.cget("text"):
                widget.destroy()

    def start(self):
        self.launch = True

    def on_closing(self):
        self.stop = True
        self._screen.destroy()
