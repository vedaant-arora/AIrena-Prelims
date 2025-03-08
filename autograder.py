import os
import time
import csv
import importlib.util
from concurrent.futures import ProcessPoolExecutor, as_completed

from agent2 import MinimaxPlayer  # Your Minimax agent
from controller import Controller  # Same Controller used in main.py

# Number of games for each board size
GAMES_PER_BOARD = 6
TIME_LIMIT = 92.0  # seconds

def dynamic_import_custom_player(agent1_path):
    """
    Dynamically import the CustomPlayer class from a given agent1.py file.
    Returns: CustomPlayer class.
    """
    spec = importlib.util.spec_from_file_location("agent1_module", agent1_path)
    agent1_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(agent1_module)
    return agent1_module.CustomPlayer

def run_single_game(board_size, player1, player2, custom_player_number=None, time_limit=92.0):
    """
    Runs a single game with the given Controller, applying a time limit if provided.
    Returns winner (1 or 2).
    """
    controller = Controller(
        board_size, 
        player1, 
        player2, 
        custom_player_number=custom_player_number, 
        time_limit=time_limit
    )
    while controller._winner == 0:
        controller.update()
    return controller._winner

def evaluate_submission(folder_name, submissions_root):
    """
    Evaluate a single submission folder (with agent1.py). Returns (folder_name, total_wins).
    The custom agent is always the 'agent1.py' role (player 2 in some games, player 1 in others),
    and has a total time limit of TIME_LIMIT seconds.
    """
    folder_path = os.path.join(submissions_root, folder_name)
    agent1_path = os.path.join(folder_path, "agent1.py")

    # If there's no agent1.py, that folder automatically gets 0 wins
    if not os.path.isfile(agent1_path):
        return (folder_name, 0)

    custom_player_class = dynamic_import_custom_player(agent1_path)
    total_wins = 0

    # Evaluate on 11×11 and 10×10, 6 games each
    board_sizes = [10, 11]
    for b_size in board_sizes:
        # 3 games: Minimax as Player1, custom as Player2
        print(f"[INFO] Evaluating '{folder_name}' on board size {b_size}...")
        for i1 in range(3):
            print(f"[INFO] Game {i1+1}/6")
           
            minimax_player = MinimaxPlayer(b_size, 1, 2)
            custom_player = custom_player_class(b_size, 2, 1)
            
            start = time.time()
            winner = run_single_game(
                board_size=b_size,
                player1=minimax_player,
                player2=custom_player,
                custom_player_number=2,      # custom is player2 for this round
                time_limit=TIME_LIMIT
            )
            elapsed = time.time() - start

            # If we haven't exceeded time AND custom_player won
            if winner == 2:
                total_wins += 1

        # 3 games: custom as Player1, Minimax as Player2
        for i2 in range(3):
            print(f"[INFO] Game {i2+4}/6")
            custom_player = custom_player_class(b_size, 1, 2)
            minimax_player = MinimaxPlayer(b_size, 2, 1)

            start = time.time()
            winner = run_single_game(
                board_size=b_size,
                player1=custom_player,
                player2=minimax_player,
                custom_player_number=1,      # custom is player1 for this round
                time_limit=TIME_LIMIT
            )
            elapsed = time.time() - start

            if winner == 1:
                total_wins += 1

    return (folder_name, total_wins)

def main():
    # Root folder containing all submission subfolders
    submissions_root = "./submission"
    
    # CSV results file
    results_file = "./results.csv"

    # Identify subfolders
    submission_folders = [
        f for f in os.listdir(submissions_root)
        if os.path.isdir(os.path.join(submissions_root, f))
    ]
    submission_folders.sort()

    # Prepare list for final results
    results_data = []

    # Process submissions in batches of 4
    batch_size = 4
    total_submissions = len(submission_folders)
    num_batches = (total_submissions + batch_size - 1) // batch_size  # Round up

    with ProcessPoolExecutor() as executor:
        for batch_index in range(num_batches):
            start_index = batch_index * batch_size
            end_index = start_index + batch_size
            chunk = submission_folders[start_index:end_index]

            print(f"\n[INFO] Starting batch {batch_index+1}/{num_batches}: {chunk}")

            # Submit tasks for this batch
            futures = {
                executor.submit(evaluate_submission, folder_name, submissions_root): folder_name
                for folder_name in chunk
            }

            # Collect results from the current batch
            for future in as_completed(futures):
                folder_name = futures[future]
                try:
                    folder_name, total_wins = future.result()
                    print(f"[INFO] Finished evaluating '{folder_name}' -> Wins: {total_wins}")
                except Exception as e:
                    print(f"[ERROR] '{folder_name}' failed: {e}")
                    folder_name, total_wins = folder_name, 0
                results_data.append((folder_name, total_wins))

            print(f"[INFO] Completed batch {batch_index+1}/{num_batches}")

    # Write CSV
    with open(results_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["folder_name", "total_wins"])
        for folder_name, wins in results_data:
            writer.writerow([folder_name, wins])

    print(f"\n[INFO] All evaluations complete. Results compiled in {results_file}")

if __name__ == "__main__":
    main()