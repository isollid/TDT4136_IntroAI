import PIL


class Board:

    def __init__(self, board, start, end):
        self.board = board
        self.start = start
        self.end = end


def make_board(path):
    board = []
    file = open(path,"r")
    line = file.readline()
    start, end = (0,0),(0,0)
    lineCount = 0
    while line != "":
        row = []

        for x in range(len(line)):
            row.append(line[x])
            if line[x] == "A": start = (lineCount,x)
            elif line[x] == "B": end = (lineCount,x)

        # Remove last line shift "\n"
        row.pop()

        board.append(row)
        lineCount += 1
        line = file.readline()

    file.close()
    return Board(board,start,end)


b = make_board("./boards/board-1-1.txt")

for line in b.board:
    print(line)

print(b.start,b.end)


