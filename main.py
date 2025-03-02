import argparse
from agent1 import RandomPlayer
from agent2 import MinimaxPlayer
from controller import Controller
from gui import GUI

def main():
    parser = argparse.ArgumentParser(description="Hexwar Game")
    parser.add_argument("--gui", type=bool, default=True, help="Enable GUI")
    parser.add_argument("--players", nargs=2, choices=["random", "minimax"], required=True, help="Player types")
    parser.add_argument("--size", type=int, default=9, help="Grid size")
    args = parser.parse_args()

    player_classes = {"random": RandomPlayer, "minimax": MinimaxPlayer}
    player1 = player_classes[args.players[0]](args.size, 1, 2)
    player2 = player_classes[args.players[1]](args.size, 2, 1)

    controller = Controller(args.size, player1, player2)

    if args.gui:
        gui = GUI(controller)
        gui.start()
        gui.run()
    else:
        while controller._winner == 0:
            controller.update()
        print(f"Player {controller._winner} wins!")

if __name__ == "__main__":
    main()
