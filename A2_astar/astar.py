from PIL import Image
from glob import glob

class Board:
    """
    Will represent a collection of the cells
    """
    def __init__(self, cells, start, end):
        self.cells = cells
        self.start = start
        self.end = end

        self.closed_nodes = []
        self.open_nodes = []

class Cell:
    """
    Will represent one node in the given board.
    """
    def __init__(self, x, y, is_wall,cost):
        self.x = x
        self.y = y
        self.is_wall = is_wall
        self.cost = cost

        self.children = []
        self.parent = None
        self.g = float('inf')   # g(s) -> cost for path so far
        self.h = None           # h(s) -> estimated value for the cost of the remaining path
        self.is_end = False

    """
    Estimated total cost for a path going through this node
    """
    def f(self):
        return self.g + self.h

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f"({self.x},{self.y},{self.is_wall})"

    def __repr__(self):
        return f"({self.x},{self.y},{self.is_wall})"


"""
Makes a board from a text file into a Board object that contains a list that hold all the cells and some other
relevant information
w Water 100
m Mountains 50
f Forests 10
g Grasslands 5
r Roads 1
"""
def make_board(path):
    costs = {"w": 100, "m": 50, "f": 10, "g": 5, "r": 1}
    cells = []
    start, end = None, None
    file = open(path,"r")
    lines = [line.strip("\n") for line in file]
    file.close()
    for y in range(len(lines)):
        for x in range(len(lines[y])):
            sign = lines[y][x]
            cost = costs[sign] if sign in costs.keys() else 1
            cell = Cell(x, y, True,cost) if sign == "#" else Cell(x,y,False,cost)
            if sign == "A":
                start = cell
                continue
            elif sign == "B":
                end = cell
            cells.append(cell)
    return Board(cells,start,end), lines


"""
Sets a the neighbours of cell.
Possible neighbours are north, east, south and west
"""
def set_all_successors(cell, possible_cells):
    for c in possible_cells:
        # Check east, south, vest and north respectfully
        if (c.x == cell.x + 1 and c.y == cell.y) or (c.x == cell.x and c.y == cell.y + 1) or\
                (c.x == cell.x - 1 and c.y == cell.y) or (c.x == cell.x and c.y == cell.y - 1):
            if not c.is_wall:
                cell.children.append(c)


"""
Finds the best path from start to end
"""
def a_star_loop(board):
    while True:
        if not board.open_nodes:
            return False  # Failed

        current_cell = board.open_nodes.pop(0)
        board.closed_nodes.append(current_cell)

        if current_cell.is_end:
            print("A* finished")
            return True # Success

        set_all_successors(current_cell,board.cells)  # Sets all the neighbours
        for successor in current_cell.children:
            if successor not in board.open_nodes and successor not in board.closed_nodes:
                attach_and_evaluate(current_cell,successor,board)
                board.open_nodes.append(successor)
                board.open_nodes.sort(key=lambda x: x.f())  # sort by the lowest estimated cost
            elif current_cell.g + successor.cost < successor.g:  # then you found a cheaper path
                attach_and_evaluate(current_cell, successor,board)
                if successor in board.closed_nodes:
                    propagate_path_improvements(successor)

"""
The attach-and-evaluate routine simply attaches a child node to a node that is now considered its best parent
(so far). The child's value of g is then computed based on the parent's value plus the cost of moving from P
to C. The heuristic value of C is assessed independently of P, and then f(C) is updated.
"""
def attach_and_evaluate(parent, child, board):
    child.parent = parent
    child.g = parent.g + child.cost
    child.h = abs(board.end.x - child.x) + abs(board.end.y - child.y)  # Manhattan-distance


"""
The propagation of path improvements recurses through the children and possibly many other descendants.
Some children may not have had P as their best parent. If the updates to g(P) do not make P the best
parent for a given child, then the propagation ceases along that child's portion of the search graph. However,
if any child can improve its own g value due to the change in g(P), then that child will have P as its best
parent and must propagate the improvement in g further, to its own children. This insures that all nodes
in the search graph are always aware of their current best parent and their current best g value, given the
information that has been uncovered by the search algorithm up to that point in time. The propagation of
these updates can eventually aect nodes on OPEN, thus in
uencing the order in which nodes get popped,
and hence the direction of search.
"""
def propagate_path_improvements(cell):
    for child in cell.children:
        if cell.g + child.cost < child.g:
            child.parent = cell
            child.g = cell.g + child.cost
            propagate_path_improvements(child)


"""
Takes a board an turn it into a png with the path from A to B visible
"""
def draw_path(board,path):
    print(f"saved to {path}")
    height = len(board)
    width = len(board[0])
    # Map from sign on board to color
    map = {"A":(255,0,0), "B":(152,0,255), ".":(255,255,255), "O":(255,255,0), "#":(0,0,0),
           "w":(60,80,255),"m": (166, 166, 166), "f": (0, 131, 0), "g": (0, 255, 114), "r": (211, 123, 59)}
    mapped = []
    for x in range(height):
        for y in range(width):
            mapped.append(map[board[x][y]])
    image = Image.new("RGB",(width,height))
    image.putdata(mapped)
    image.save(path)


"""
Method for using astar and making image from one text file
"""
def find_shortpath_make_img(board_path):
    # Build the board
    board, old_text_board = make_board(board_path)
    # Set some init values
    start, end = board.start, board.end
    end.is_end = True
    start.h = abs(end.x - start.x) + abs(end.y - start.y)  # Manhattan-distance
    start.g = 0
    board.open_nodes.append(start)

    # Draw result if a_star succeed
    if a_star_loop(board):
        # Start in the end, and get the parent backwards to start
        cell = board.end
        # I make a copy so that it easy to compare the unsolved board with the solved board
        copy = old_text_board.copy()
        wall = ["#"*len(copy[0])]  # Used to separate the unsolved board and the solved board
        while cell.parent != start:
            row = list(old_text_board[cell.parent.y])
            row[cell.parent.x] = 'O'
            old_text_board[cell.parent.y] = ''.join(row)
            cell = cell.parent

        # If you want to se the board toString
        #lines = '\n'.join(old_text_board)
        #print(lines)

        draw_path(copy+wall+old_text_board, "img/" + board_path.split("/")[2].split(".")[0] + ".png")
    else:
        print('A* failed')


def main():
    # Loop over all the txt files, use astar, and draw boards
    files = glob("./boards/*")
    for path in files:
        find_shortpath_make_img(path)

main()


