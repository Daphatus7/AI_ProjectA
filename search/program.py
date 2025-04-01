# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part A: Single Player Freckers
import heapq

from .core import CellState, Coord, Direction, MoveAction, BOARD_N
from .utils import render_board

class Node:
    def __init__(self, coord, parent):
        self.coord = coord
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0
        self.move = None
        self.is_jump = False
    def __eq__(self, other):
        return self.coord == other.coord
    def __lt__(self, other):
        return self.f < other.f

def search(
    board: dict[Coord, CellState]
) -> list[MoveAction] | None:
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

    # The render_board() function is handy for debugging. It will print out a
    # board state in a human-readable format. If your terminal supports ANSI
    # codes, set the `ansi` flag to True to print a colour-coded version!
    print(render_board(board, ansi=True))
    #find the start and end coordinates
    #start
    start = None
    for coord in board:
        if board[coord] == CellState.RED:
            start = coord

    ends = []
    for i in range(BOARD_N):
        candidate = Coord(BOARD_N - 1, i)
        if valid_landing_spot(board, candidate):
            ends.append(candidate)

    if ends is not None:
        #pathfinding
        path = pathfinding(board, start, ends)
        if path is not None:
            return path
        #[Coord, Direction]
    return None

#a* search
def pathfinding(board: dict[Coord, CellState], start:[Coord] , ends :[[Coord]]) \
        -> list[MoveAction] | None:
    action_list = [] # list of actions and sorted by f value
    closed_list = set()

    #create the start node
    start_node = Node(start, None)

    #also filter out the ends that are not valid landing spots
    end_nodes = [Node(end,None) for end in ends if valid_landing_spot(board, end)]

    #the current node
    heapq.heappush(action_list, start_node)

    #continue exploring until open list is empty
    while len(action_list) > 0:
        # explore the node with the lowest f value
        current = heapq.heappop(action_list)#get the node with smallest f value
        #copy the board
        board = board.copy()
        board[current.coord] = CellState.RED
        print(render_board(board, ansi=True))
        # mark the current node as explored
        closed_list.add(current.coord)

        #check if current is the end
        if current.coord in ends:
            #repack the path to return
            print("found path" + str(current.coord))
            return retrace_path(current)

        # all possible directions
        for direction in red_directions():
            r_vector, c_vector = current.coord.r + direction.r, current.coord.c + direction.c
            if is_on_board(r_vector, c_vector):
                next_coord = Coord(r_vector, c_vector)
                if next_coord not in closed_list: # is not explored
                    print("checking node " + str(next_coord))
                    if can_jump(board, next_coord, direction): # if it can jump
                        print("can jump " + str(next_coord))
                        new_node = Node(next_coord + direction, current)
                        new_node.g = current.g
                        new_node.h = h_cost(new_node.coord, end_nodes)
                        new_node.f = new_node.g + new_node.h
                        #if parent is not jump_start then mark this as jump_start:
                        new_node.is_jump = True
                        new_node.move = direction
                        add_new_node(action_list, new_node)
                    #if it cannot jump check if is a valid landing spot
                    elif valid_landing_spot(board, next_coord):
                        print("can land" + str(next_coord))
                        new_node = Node(next_coord, current)
                        new_node.g = current.g + 1
                        new_node.h = h_cost(new_node.coord, end_nodes)
                        new_node.f = new_node.g + new_node.h
                        new_node.move = direction
                        add_new_node(action_list, new_node)
                    else:
                        print("not valid landing spot" + str(next_coord))
                        continue


#if it is blue then it is another way around
def red_directions():
    return [Direction.Down, Direction.DownLeft, Direction.DownRight, Direction.Left, Direction.Right]

def add_new_node(action_list, new_node):
    heapq.heappush(action_list, new_node)
def is_on_board(r,c):
    return 0 <= r < BOARD_N and 0 <= c < BOARD_N

def can_jump(board, new_coord, direction):
    # Check if the position exists and contains a blue frog
    if new_coord not in board or board[new_coord] != CellState.BLUE:
        return False
        
    # Calculate landing spot after jumping
    landing_r, landing_c = new_coord.r + direction.r, new_coord.c + direction.c
    
    # First check if landing is within board boundaries
    if not is_on_board(landing_r, landing_c):
        return False
        
    landing_coord = Coord(landing_r, landing_c)
    # Then check if it's a valid lily pad
    if landing_coord in board and board[landing_coord] == CellState.LILY_PAD:
        return True
    return False

#heuristic function
def h_cost(start : Coord, ends : []) -> int:
    return min(abs(start.r - end.coord.r) + abs(start.c - end.coord.c) for end in ends)

def valid_landing_spot(board, coord):
    #check position is valid
    if coord not in board:
        return False
    #check valid pad
    if board[coord] == CellState.LILY_PAD and board[coord] != CellState.RED and board[coord] != CellState.BLUE:
        return True

def retrace_path(end_node: Node) -> list[MoveAction]:
    # Empty list to store the path
    path = []
    # Traverse the linked list
    cur_node = end_node
    while cur_node:
        print("cur_node " + str(cur_node.coord))
        if cur_node.is_jump:
            # Collect jump moves
            moves = [cur_node.move]
            # Move backwards through jump nodes to find the jump start
            while cur_node.parent and cur_node.parent.is_jump:
                cur_node = cur_node.parent
                moves.append(cur_node.move)
            # Collect the node coord
            jump_start_coord = cur_node.parent.coord if cur_node.parent else cur_node.coord
            moves.reverse()
            path.append(MoveAction(jump_start_coord, moves))
            cur_node = cur_node.parent
        else:
            # Normal single move
            if cur_node.parent:
                direction = cur_node.move if cur_node.move else None
                if direction:
                    path.append(MoveAction(cur_node.parent.coord, [direction]))
            cur_node = cur_node.parent
    path.reverse()
    return path
