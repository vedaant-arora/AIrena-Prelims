import numpy as np
from agent import Agent

class CustomPlayer(Agent):
    def __init__(self, size, player_number, adv_number):
        super().__init__(size, player_number, adv_number)
        self.name = "HexMaster"
        self.max_depth = 3  # Deeper search than agent2
        
    def step(self):
        # First move optimization - if we're player 1, take center as it's strong in Hex
        if len(self.free_moves()) == self.size * self.size:
            if self.player_number == 1:  # Player 1 connects horizontally
                move = [self.size // 2, self.size // 2]
                self.set_hex(self.player_number, move)
                return move
        
        # Look for immediate winning moves
        for move in self.free_moves():
            test_board = self.copy()
            test_board.set_hex(self.player_number, move)
            if test_board.check_win(self.player_number):
                self.set_hex(self.player_number, move)
                return move
                
        # Look for moves that block opponent's win
        for move in self.free_moves():
            test_board = self.copy()
            test_board.set_hex(self.adv_number, move)
            if test_board.check_win(self.adv_number):
                self.set_hex(self.player_number, move)
                return move
                
        # Use minimax with alpha-beta pruning for regular moves
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        for move in self.free_moves():
            new_board = self.copy()
            new_board.set_hex(self.player_number, move)
            value = self.minimax(new_board, self.max_depth, alpha, beta, False)
            if value > best_value:
                best_value = value
                best_move = move
            alpha = max(alpha, best_value)
        
        if best_move is None:  # Fallback to first available move
            best_move = self.free_moves()[0]
        
        self.set_hex(self.player_number, best_move)
        return best_move

    def update(self, move_other_player):
        self.set_hex(self.adv_number, move_other_player)
    
    def minimax(self, board, depth, alpha, beta, is_maximizing):
        # Check for terminal conditions
        if board.check_win(self.player_number):
            return 1000 + depth  # Winning sooner is better
        if board.check_win(self.adv_number):
            return -1000 - depth  # Losing later is better
        if depth == 0 or len(board.free_moves()) == 0:
            return self.evaluate_board(board)
        
        if is_maximizing:
            value = float('-inf')
            for move in board.free_moves()[:min(len(board.free_moves()), 7)]:  # Limit branching
                new_board = board.copy()
                new_board.set_hex(self.player_number, move)
                value = max(value, self.minimax(new_board, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        else:
            value = float('inf')
            for move in board.free_moves()[:min(len(board.free_moves()), 7)]:  # Limit branching
                new_board = board.copy()
                new_board.set_hex(self.adv_number, move)
                value = min(value, self.minimax(new_board, depth - 1, alpha, beta, True))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value
    
    def evaluate_board(self, board):
        """
        Sophisticated board evaluation specialized for Hex
        """
        # Calculate our connectivity score
        player_score = self.connectivity_score(board, self.player_number)
        
        # Calculate opponent's connectivity score
        opponent_score = self.connectivity_score(board, self.adv_number)
        
        # Calculate edge connectivity (critical in Hex)
        player_edge = self.edge_connectivity(board, self.player_number)
        opponent_edge = self.edge_connectivity(board, self.adv_number)
        
        # Combine scores with appropriate weights
        return (player_score * 1.0 + player_edge * 2.0) - (opponent_score * 1.2 + opponent_edge * 2.2)
    
    def connectivity_score(self, board, player):
        """Score based on the size and quality of connected groups"""
        score = 0
        visited = set()
        
        for x in range(board.size):
            for y in range(board.size):
                coord = (x, y)
                if coord not in visited and board.get_hex([x, y]) == player:
                    group, group_size = self._get_connected_group(board, [x, y], player)
                    visited.update(group)
                    
                    # Group size squared (larger groups are exponentially better)
                    score += group_size * group_size
                    
                    # Extra points for groups with many neighbors
                    empty_neighbors = self._count_empty_neighbors(board, group)
                    score += empty_neighbors * 2
        
        return score
    
    def edge_connectivity(self, board, player):
        """Score edge connections based on player's goals"""
        score = 0
        
        if player == 1:  # Connects left to right (x=0 to x=size-1)
            left_edge = sum(1 for y in range(board.size) if board.get_hex([0, y]) == player)
            right_edge = sum(1 for y in range(board.size) if board.get_hex([board.size-1, y]) == player)
            
            # Check for diagonal pattern from edges (very effective in Hex)
            for y in range(board.size):
                if board.get_hex([0, y]) == player:
                    # Look for pieces extending diagonally from left edge
                    for i in range(1, min(board.size, 4)):
                        if y+i < board.size and board.get_hex([i, y+i]) == player:
                            score += 5
                            
            for y in range(board.size):
                if board.get_hex([board.size-1, y]) == player:
                    # Look for pieces extending diagonally from right edge
                    for i in range(1, min(board.size, 4)):
                        if y+i < board.size and board.get_hex([board.size-1-i, y+i]) == player:
                            score += 5
            
            score += left_edge * 10 + right_edge * 10
            
        else:  # Connects top to bottom (y=0 to y=size-1)
            top_edge = sum(1 for x in range(board.size) if board.get_hex([x, 0]) == player)
            bottom_edge = sum(1 for x in range(board.size) if board.get_hex([x, board.size-1]) == player)
            
            # Check for diagonal pattern from edges
            for x in range(board.size):
                if board.get_hex([x, 0]) == player:
                    # Look for pieces extending diagonally from top edge
                    for i in range(1, min(board.size, 4)):
                        if x+i < board.size and board.get_hex([x+i, i]) == player:
                            score += 5
                            
            for x in range(board.size):
                if board.get_hex([x, board.size-1]) == player:
                    # Look for pieces extending diagonally from bottom edge
                    for i in range(1, min(board.size, 4)):
                        if x+i < board.size and board.get_hex([x+i, board.size-1-i]) == player:
                            score += 5
            
            score += top_edge * 10 + bottom_edge * 10
            
        return score
    
    def _get_connected_group(self, board, start, player):
        """Find all coordinates in a connected group"""
        group = set([(start[0], start[1])])
        frontier = [start]
        
        while frontier:
            current = frontier.pop()
            for neighbor in board.neighbors(current):
                neighbor_tuple = (neighbor[0], neighbor[1])
                if board.get_hex(neighbor) == player and neighbor_tuple not in group:
                    group.add(neighbor_tuple)
                    frontier.append(neighbor)
        
        return group, len(group)
    
    def _count_empty_neighbors(self, board, group):
        """Count empty neighbors of a group"""
        empty_neighbors = set()
        
        for x, y in group:
            for neighbor in board.neighbors([x, y]):
                if board.get_hex(neighbor) == 0:  # Empty cell
                    empty_neighbors.add((neighbor[0], neighbor[1]))
        
        return len(empty_neighbors)