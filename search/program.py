# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part A: Single Player Freckers

import heapq
from .core import CellState, Coord, Direction, MoveAction, BOARD_N
from .utils import render_board


# Node class to represent each state in the A* search
class Node:
    def __init__(self, coord, parent):
        self.coord = coord      # Coordinates of the node
        self.parent = parent    # Parent node for backtracking
        self.g = 0              # Cost from start to this node
        self.h = 0              # Heuristic cost to the end node
        self.f = 0              # Total cost (g + h)
        self.move = None        # Direction of the move
        self.is_jump = False    # Flag to indicate if this node is a jump start
    
    def __eq__(self, other): 
        return self.coord == other.coord
    
    def __lt__(self, other):
        return self.f < other.f


# Entry point for the search of the shortest path
def search(board: dict[Coord, CellState]) -> list[MoveAction] | None:
    """
    This is the entry point for your submission. You should modify this
    function to solve the search problem discussed in the Part A specification.
    See `core.py` for information on the types being used here.

    Parameters:
        `board`: a dictionary representing the initial board state, mapping
            coordinates to "player colours". The keys are `Coord` instances,
            and the values are `CellState` instances which can be one of
            `CellState.RED`, `CellState.BLUE`, or `CellState.LILY_PAD`.

    Returns:
        A list of "move actions" as MoveAction instances, or `None` if no
        solution is possible.
    """
    # Print the board for better visualization
    print(render_board(board, ansi=True))
    
    # Find the starting position of the red frog
    start = None
    for coord in board:
        if board[coord] == CellState.RED:
            start = coord
            break
    if start is None:
        return None

    # Find all possible ending positions for the red frog
    ends = []
    for i in range(BOARD_N):
        candidate = Coord(BOARD_N - 1, i)
        if valid_landing_spot(board, candidate):
            ends.append(candidate)

    if ends is not None:
        # Search for the path
        path = pathfinding(board, start, ends)
        if path is not None:
            return path
    return None


# A* search algorithm
def pathfinding(
    board: dict[Coord, CellState], 
    start: Coord, 
    ends: list[Coord]
) -> list[MoveAction] | None:
    
    action_list = []       # List of actions sorted by f value
    closed_list = set()    # Set of explored nodes

    # Begin search from the starting position
    start_node = Node(start, None)
    heapq.heappush(action_list, start_node)

    # Continue exploring until open list is empty
    while len(action_list) > 0:
        # Explore the node with the lowest f value
        current = heapq.heappop(action_list)  # Get the node with smallest f value
        board = board.copy()
        board[current.coord] = CellState.RED
        # Debug board state
        # print(render_board(board, ansi=True))
        
        # Mark the current node as explored
        closed_list.add(current.coord)

        # Check if current is the end
        if current.coord in ends:
            # Debug path found
            # print("Found path" + str(current.coord))
            return retrace_path(current)

        # All possible directions
        for direction in red_directions():
            r_vector = current.coord.r + direction.r
            c_vector = current.coord.c + direction.c
            
            if is_on_board(r_vector, c_vector):
                next_coord = Coord(r_vector, c_vector)
                
                if next_coord not in closed_list:  # Is not explored
                    # Debug node checking
                    # print("Checking node " + str(next_coord))
                    
                    if can_jump(board, next_coord, direction):  # If it can jump
                        # Debug jump
                        # print("Can jump " + str(next_coord))
                        new_node = Node(next_coord + direction, current)
                        new_node.g = current.g
                        new_node.h = h_cost(new_node.coord, ends)
                        new_node.f = new_node.g + new_node.h
                        new_node.is_jump = True
                        new_node.move = direction
                        add_new_node(action_list, new_node)
                    
                    # If it cannot jump check if is a valid landing spot
                    elif valid_landing_spot(board, next_coord):
                        # Debug landing
                        # print("Can land" + str(next_coord))
                        new_node = Node(next_coord, current)
                        new_node.g = current.g + 1
                        new_node.h = h_cost(new_node.coord, ends)
                        new_node.f = new_node.g + new_node.h
                        new_node.move = direction
                        add_new_node(action_list, new_node)
                    
                    else:
                        # Debug invalid spot
                        # print("Not valid landing spot" + str(next_coord))
                        continue


# Valid movement directions for Red frog
def red_directions():
    return [
        Direction.Down, 
        Direction.DownLeft, 
        Direction.DownRight, 
        Direction.Left, 
        Direction.Right
    ]


def add_new_node(action_list, new_node):
    heapq.heappush(action_list, new_node)


# Check if the coordinates are within the board boundaries
def is_on_board(r, c):
    return 0 <= r < BOARD_N and 0 <= c < BOARD_N


# Check if red frog can jump over a blue frog in a given direction
def can_jump(board, new_coord, direction):
    # Check if the position exists and contains a blue frog
    if new_coord not in board or board[new_coord] != CellState.BLUE:
        return False
        
    # Calculate landing position and check boundaries
    landing_r = new_coord.r + direction.r
    landing_c = new_coord.c + direction.c
    
    if not is_on_board(landing_r, landing_c):
        return False
    
    # Verify landing spot is a lily pad
    landing_coord = Coord(landing_r, landing_c)
    return (landing_coord in board and 
            board[landing_coord] == CellState.LILY_PAD)


# Manhattan distance heuristic - minimum distance to any end position
def h_cost(start: Coord, ends: list[Coord]) -> int:
    return min(abs(start.r - end.r) + abs(start.c - end.c) for end in ends)


# Check if position is a valid landing spot
def valid_landing_spot(board, coord):
    if coord not in board:
        return False
    return (board[coord] == CellState.LILY_PAD and 
            board[coord] != CellState.RED and 
            board[coord] != CellState.BLUE)

# Reconstruct path from end node to start, handling both jumps and single moves
def retrace_path(end_node):
    path = []
    current = end_node  # Start from the goal node
    
    while current:
        # Case 1: Handle jump sequences (multiple connected jumps)
        if current.is_jump:
            jump_moves = []
            
            # Collect all consecutive jumps in reverse order
            while current and current.is_jump:
                jump_moves.append(current.move)
                current = current.parent
            
            if jump_moves:
                # Reverse to get correct order and package as one MoveAction
                jump_moves.reverse()
                start_coord = current.coord if current else jump_moves[0]
                path.append(MoveAction(start_coord, jump_moves))
                continue  # Skip the regular move handling below
        
        # Case 2: Handle regular single moves
        if current.parent and current.move:
            path.append(MoveAction(current.parent.coord, [current.move]))
        
        current = current.parent
    
    return path[::-1]  # Return in start-to-goal order