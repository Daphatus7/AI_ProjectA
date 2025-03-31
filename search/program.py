# COMP30024 Artificial Intelligence, Semester 1 2025
# Project Part A: Single Player Freckers
import heapq

from .core import CellState, Coord, Direction, MoveAction
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
    for i in range(8):
        candidate = Coord(7, i)
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
def pathfinding(board: dict[Coord, CellState], start:[Node] , ends :[[Coord]]) \
        -> list[MoveAction] | None:
    action_list = [] # list of actions and sorted by f value
    closed_list = set()

    #create the start node
    start_node = Node(start, None)

    #also filter out the ends that are not valid landing spots
    end_nodes = [Node(end,None) for end in ends if valid_landing_spot(board, end)]

    #the current node
    action_list.append(start_node)

    #continue exploring until open list is empty
    while len(action_list) > 0:
        # explore the node with the lowest f value
        current = action_list.pop(0)#get the node with smallest f value

        # mark the current node as explored
        closed_list.add(current.coord)

        #check if current is the end
        if current.coord in ends:
            #repack the path to return
            return retrace_path(current)

        # all possible directions
        for direction in red_directions():
            next_coord = current.coord + direction
            #if it can jump
            if next_coord not in closed_list: # is not explored
                #add the next node to the open list
                if can_jump(board, next_coord, direction): # if it can jump
                    new_node = Node(next_coord + direction, current)
                    new_node.g = current.g
                    new_node.h = h_cost(new_node.coord, end_nodes)
                    new_node.f = new_node.g + new_node.h
                    #if parent is not jump_start then mark this as jump_start:
                    new_node.is_jump = True
                    new_node.move = direction
                    add_new_node(action_list, new_node)
                #if it cannot jump
                elif valid_landing_spot(board, next_coord):
                    new_node = Node(next_coord, current)
                    new_node.g = current.g + 1
                    new_node.h = h_cost(new_node.coord, end_nodes)
                    new_node.f = new_node.g + new_node.h
                    new_node.move = direction
                    add_new_node(action_list, new_node)
                else:
                    continue


#if it is blue then it is another way around
def red_directions():
    return [Direction.Down, Direction.DownLeft, Direction.DownRight, Direction.Left, Direction.Right]

def add_new_node(action_list, new_node):
    action_list.append(new_node)
    action_list.sort(key=lambda x: x.f)

def can_jump(board, new_coord, direction):
    #check if there is a frog
    if new_coord not in board:
        return False
    if board[new_coord] == CellState.BLUE:
        if (new_coord + direction) in board and board[new_coord + direction] == CellState.LILY_PAD:
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
