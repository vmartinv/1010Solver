import random, time, datetime
import curses

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class InvalidMoveException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
class Piece:
    """A list of tuples that contain the coordinates of the blocks in a piece,
    in respect to the left most block in the top row of a piece. This block is represented by (0,0)."""
    def __init__(self, blocks, name, char_rep, input_position):
        self.blocks = blocks
        self.name = name
        self.char_rep = char_rep
        self.input_position = input_position
    # as an example, a piece that is three blockshly would be [(0,0),(1,0),(2,0)]

    def __str__(self):
        out = ""
        x_offset = 0
        y_offset = 0
        width = 0
        height = 0
        for block in self.blocks:
            width = max(width, block[0]+1)
            height = max(height, block[1]+1)
            x_offset = max(x_offset,-block[0])
            y_offset = max(y_offset,-block[1])
        width += x_offset
        height += y_offset
        for y in range(height):
            for x in range(width):
                if (x-x_offset,y-y_offset) in self.blocks:
                    out += self.char_rep.upper()
                else:
                    out += ' '
            out += '\n'
        return out
        
    def show(self, win, p):
        (y, x) = p
        for i,l in enumerate(str(self).split('\n')):
            win.addstr(y+i, x, l)

class Move:
    def __init__(self, piece, x, y):
        self.piece = piece
        self.x = x
        self.y = y

    def __str__(self):
        return "{} at {},{}".format(self.piece.name,self.x,self.y)

    def __repr__(self):
        return '\n' + str(self)

    def export_as_str(self):
        return chr((10*self.y+self.x)+32)+ self.piece.char_rep

def import_move_as_str(string):
    return Move(piece_dict[string[1]], (ord(string[0])-32)%10, ((ord(string[0])-32)//10))



class Board:
    """A 10 x 10 list of 0's and 1's, 0 means a space is clear, 1 means it's occupied. Represents a gamestate of the 10 x 10 board
    On this board, the coordinates system starts with (0,0) being the top left corner, and the first coordinate being the x, and the second being the y."""
    # EMPTY_BOARD = [[0] * 10 for x in range(10)]
    """Constructs a Board. Default is empty"""
    def __init__(self, matrix = None, current_pieces = [], move_str = ''):
        if matrix == None:
            self.matrix = [[0] * 10 for x in range(10)]
        else:
            self.matrix = matrix
        self.last_piece = [[0] * 10 for x in range(10)]
        self.current_pieces = current_pieces[:]
        self.move_str = ''


    def copy(self):
        """Returns a new board identical to self"""
        new_matrix = []
        for col in self.matrix:
            new_matrix.append(col[:])
        return Board(new_matrix, self.current_pieces[:], self.move_str[:])

    """Returns True if you can place Piece p at the Location loc"""
    def is_valid_move(self, move):
        if not move.piece in self.current_pieces:
            return False
        for block in move.piece.blocks:
            currX, currY = block[0] + move.x, block[1] + move.y
            if currX not in range(10) or currY not in range(10) or self.matrix[currX][currY] != 0:
                return False
        return True

    def get_valid_moves(self):
        out = []
        for piece in self.current_pieces:
            for x in range(10):
                for y in range(10):
                    move = Move(piece, x, y)
                    if self.is_valid_move(move):
                        out.append(move)
        return out

    def get_valid_moves_2(self, piece):
        out = []
        for x in range(10):
            for y in range(10):
                move = Move(piece, x, y)
                if self.is_valid_move(move):
                    out.append(move)
        return out

    def has_valid_moves(self):
        for piece in self.current_pieces:
            for x in range(10):
                for y in range(10):
                    move = Move(piece, x, y)
                    if self.is_valid_move(move):
                        return True
        return False


    """Returns a list of numbers containing the numbers of the rows that are currently full in the board"""
    def get_full_rows(self):
        output = []
        for y in range(10):
            found0 = False
            for x in range(10):
                if self.matrix[x][y] == 0:
                    found0 = True
                    break
            if not found0:
                output.append(y)
        return output

    """Returns a list of numbers containing the numbers of the columns that are currently full in the board"""
    def get_full_cols(self):
        output = []
        for x in range(10):
            if 0 not in self.matrix[x]:
                output.append(x)
        return output


    """Places a piece p at a space loc (given by a tuple with two coordinates), updates board accordingly
        Returns a tuple of two lists that contains rows and cols cleared respectively"""
    def make_move(self, move):
        if self.is_valid_move(move):
            self.last_piece = [[0] * 10 for x in range(10)]
            move_str = move.export_as_str()
            # placing piece
            for block in move.piece.blocks:
                self.matrix[block[0] + move.x][block[1] + move.y] = 1
                self.last_piece[block[0] + move.x][block[1] + move.y] = 1
            # clearing appropriate rows/cols
            full_rows, full_cols = self.get_full_rows(), self.get_full_cols()
            for y in full_rows:
                move_str += "{}y".format(y)
                for x in range(10):
                    if not (x in full_cols):
                        self.matrix[x][y] -= 1
                        self.last_piece[x][y] = 2
            for x in full_cols:
                move_str += "{}x".format(x)
                for y in range(10):
                    self.matrix[x][y] -= 1
                    self.last_piece[x][y] = 3
            for block in move.piece.blocks:
                self.last_piece[block[0] + move.x][block[1] + move.y] = 1
            self.current_pieces.remove(move.piece)
            self.move_str += move_str
            return full_rows, full_cols
        else:
            print("Here is a string representing the current board:")
            print(self.export_as_str())
            raise InvalidMoveException('{} is not a valid move'.format(move))

    """Places a piece p at a space loc (given by a tuple with two coordinates), updates board accordingly
        Returns a tuple of two lists that contains rows and cols cleared respectively"""
    def force_move(self, move):
        self.last_piece = [[0] * 10 for x in range(10)]
        # placing piece
        move_str = move.export_as_str()
        for block in move.piece.blocks:
            self.matrix[block[0] + move.x][block[1] + move.y] = 1
            self.last_piece[block[0] + move.x][block[1] + move.y] = 1
        # clearing appropriate rows/cols
        full_rows, full_cols = self.get_full_rows(), self.get_full_cols()
        for y in full_rows:
            move_str += "{}y".format(y)
            for x in range(10):
                if not (x in full_cols):
                    self.matrix[x][y] -= 1
                    self.last_piece[x][y] = 2
        for x in full_cols:
            move_str += "{}x".format(x)
            for y in range(10):
                self.matrix[x][y] -= 1
                self.last_piece[x][y] = 3
        # self.current_pieces.remove(move.piece)
        self.move_str += move_str
        return full_rows, full_cols


    def draw_input(self, win):
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        win.erase()
        for piece in piece_list:
            piece.show(win, piece.input_position)
        win.addstr(19, 0, "#"*41)
        for i,p in enumerate(self.current_pieces):
            p.show(win, (21, i*15))
        win.addstr(26, 0, '       ')
        if len(self.current_pieces) == 3:
            win.addstr('[OK]', curses.color_pair(2))
        else:
            win.addstr('    ')
        win.addstr('       ')
        win.addstr('[REINICIAR]', curses.color_pair(1))
        win.addstr(' ')
        win.refresh()

    def add_to_pieces(self, piece):
        while len(self.current_pieces)>=3:
            del self.current_pieces[0]
        self.current_pieces.append(piece)

    def refresh_pieces(self, win):
        self.last_piece = [[0] * 10 for x in range(10)]
        self.current_pieces = []
        while True:
            self.draw_input(win)
            win.keypad(1)
            curses.halfdelay(1)
            event = win.getch()
            if (event == curses.KEY_ENTER or event == 10 or event == 13) and len(self.current_pieces) == 3:
                return
            for piece in piece_list:
                if event == ord(piece.char_rep):
                    self.add_to_pieces(piece)
            if event == curses.KEY_MOUSE:
                _, x, y, _, bstate = curses.getmouse()
                if bstate & curses.BUTTON1_CLICKED:
                    if y==26 and 18<=x and x<=28:
                        self.current_pieces = []
                    elif y==26 and 7<=x and x<=10 and len(self.current_pieces) == 3:
                        return
                    for piece in piece_list:
                        if (x-piece.input_position[1], y-piece.input_position[0]) in piece.blocks:
                            self.add_to_pieces(piece)

    def export_as_str(self):
        out = ''
        for x in range(10):
            for y in range(10):
                out += str(self.matrix[x][y])
        for piece in self.current_pieces:
            out += piece.char_rep
        return out

    def import_as_str(self, input_str):
        for x in range(10):
            for y in range(10):
                self.matrix[x][y] = int(input_str[x*10+y])
        for char in input_str[100:]:
            self.current_pieces.append(piece_dict[char])

    def undo_move(self):
        "undoes the last move based on the board's move_str"
        self.last_piece = [[0] * 10 for x in range(10)]
        index = len(self.move_str) -1
        # print "BEFORE"
        # print self.move_str
        decreased = []
        last_char = self.move_str[index]
        while last_char == 'x' or last_char == 'y':
            if  last_char == 'x':
                for y in range(10):
                    if not ((int(self.move_str[index-1]), y) in decreased):
                        decreased.append((int(self.move_str[index-1]), y))
                        self.matrix[int(self.move_str[index-1])][y] += 1
            elif last_char == 'y':
                for x in range(10):
                    if not ((x, int(self.move_str[index-1])) in decreased):
                        decreased.append((x, int(self.move_str[index-1])))
                        self.matrix[x][int(self.move_str[index-1])] += 1
            index -= 2
            last_char = self.move_str[index]
        move = import_move_as_str(self.move_str[index - 1:index + 1])
        for block in move.piece.blocks:
            self.matrix[block[0] + move.x][block[1] + move.y] = 0
        self.current_pieces.append(move.piece)
        self.move_str = self.move_str[:index - 1]
        # print "AFTER"
        # print self.move_str

    # def import_move_str(self, move_str):
    #     while x <
    #     curr_pair = move_str
    def interact(self, win):
        while True:
            self.show(win)
            win.keypad(1)
            curses.halfdelay(1)
            event = win.getch()
            if event == curses.KEY_ENTER or event == 10 or event == 13:
                return
            if event == curses.KEY_MOUSE:
                _, x, y, _, bstate = curses.getmouse()
                xM = (x-1)/4
                yM = (y-2)/2
                if bstate & curses.BUTTON1_CLICKED:
                    if y==26 and 18<=x and x<=27 and self.move_str:
                        while len(self.current_pieces)<3:
                            self.undo_move()
                        self.current_pieces = []
                    elif y==26 and 7<=x and x<=10:
                        return
                    if 0<=xM and xM <10 and 0<=yM and yM <10:
                        self.matrix[xM][yM]+=1
                elif bstate & curses.BUTTON3_CLICKED:
                    if 0<=xM and xM <10 and 0<=yM and yM <10:
                        self.matrix[xM][yM]-=1

    def show(self, win):
        win.erase()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)
        win.addstr(0, 0, " ")
        for i in range(10):
            win.addstr(" {}  ".format(i))
        win.addstr('\n')
        for y in range(10):
            win.addstr(' '+'-' * 41 + '\n')
            win.addstr('{}|'.format(y))
            for x in range(10):
                if self.matrix[x][y] == 0:
                    if self.last_piece[x][y] == 0:
                        win.addstr('  ', curses.color_pair(3))
                    else:
                        win.addstr('  ', curses.color_pair(2))
                elif self.matrix[x][y] == 1:
                    if self.last_piece[x][y] == 0:
                        win.addstr(' X', curses.color_pair(3))
                    elif self.last_piece[x][y] >= 2:
                        win.addstr(' X', curses.color_pair(2))
                    else:
                        win.addstr(' X', curses.color_pair(1))
                elif self.matrix[x][y] <10:
                    if self.last_piece[x][y] == 0:
                        win.addstr(' ' + str(self.matrix[x][y]), curses.color_pair(3))
                    elif self.last_piece[x][y] >= 2:
                        win.addstr(' ' + str(self.matrix[x][y]), curses.color_pair(2))
                    else:
                        win.addstr(' ' + str(self.matrix[x][y]), curses.color_pair(1))
                else:
                    if self.last_piece[x][y] == 0:
                        win.addstr(str(self.matrix[x][y]), curses.color_pair(3))
                    elif self.last_piece[x][y] >= 2:
                        win.addstr(str(self.matrix[x][y]), curses.color_pair(2))
                    else:
                        win.addstr(str(self.matrix[x][y]), curses.color_pair(1))
                win.addstr(' |')
            win.addstr('\n')
        win.addstr(' '+'-' * 41)
        win.addstr(26, 0, '       ')
        win.addstr('[OK]', curses.color_pair(2))
        if self.move_str:
            win.addstr('       ')
            win.addstr('[DESHACER]', curses.color_pair(1))
        win.refresh()




# All possible pieces
piece_list = [
Piece([(0,0)],'1', 'a', (17, 35)), #singleton
Piece([(0,0),(1,0)],'2h', 'b', (0, 0)), #2h
Piece([(0,0),(1,0),(2,0)],'3h', 'c', (2, 0)), #3h
Piece([(0,0),(1,0),(2,0),(3,0)],'4h', 'd', (4, 0)), #4h
Piece([(0,0),(1,0),(2,0),(3,0),(4,0)], '5h', 'e', (6, 0)), #5h
Piece([(0,0),(0,1)], '2v', 'f', (0, 18)), #2v
Piece([(0,0),(0,1),(0,2)], '3v', 'g', (0, 24)), #3v
Piece([(0,0),(0,1),(0,2),(0,3)], '4v', 'h', (0, 30)), #4v
Piece([(0,0),(0,1),(0,2),(0,3),(0,4)], '5v', 'i', (0, 36)), #5v
Piece([(0,0),(0,1),(1,1)], 'l', 'j', (8, 1)), #l
Piece([(1,0),(1,1),(0,1)], 'l1', 'k', (8, 11)), #l mirrored
Piece([(0,0),(0,1),(1,0)], 'l3', 'l', (8, 23)), #l flipped
Piece([(0,0),(1,1),(1,0)], 'l2', 'm', (8, 35)), #l mirrored flipped
Piece([(0,0),(0,1),(0,2),(1,2),(2,2)], 'L', 'n', (11, 0)), #L
Piece([(2,0),(2,1),(2,2),(1,2),(0,2)], 'L1', 'o', (11, 11)), #L mirrored
Piece([(0,0),(0,1),(0,2),(1,0),(2,0)], 'L3', 'p', (11, 22)), #l flipped
Piece([(0,0),(2,1),(2,2),(1,0),(2,0)], 'L2', 'q', (11, 35)), #l mirrored flipped
Piece([(0,0),(0,1),(1,0),(1,1)], '4', 'r', (16, 18)), #2x2
Piece([(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),(2,0),(2,1),(2,2)], '9', 's', (15, 0)) #3x3
]
import string
piece_dict = dict(zip(string.ascii_lowercase, piece_list))



class Result:
    """Class that defines result of a run, and includes the score, the move string,
    time stamp, and a list of strings that are tags that can be aggregated"""
    def __init__(self, score, timestamp, length, move_str, tags):
        self.score = score
        self.move_str = move_str
        self.tags = tags
        self.timestamp = timestamp
        self.length = length

def play(win, get_move, verbose = True):
    move_num = 1
    cleared_lines = 0
    score = 0
    board = Board()


    board.interact(win)
    board.refresh_pieces(win)

    while board.has_valid_moves():
        board.show(win)
        win.addstr(26, 2, 'Pensando...                  ')
        win.refresh()
        move = get_move(board)
        # try:
        cleared_rows, cleared_cols = board.make_move(move)
        score += len(move.piece.blocks)
        #~ if verbose:
            #~ print("{}placed at {},{}".format(move.piece,move.x,move.y))
            #~ if cleared_cols != []:
                #~ for col in cleared_cols:
                    #~ print("Cleared Column {}!".format(col))
            #~ if cleared_rows != []:
                #~ for row in cleared_rows:
                    #~ print("Cleared Row {}!".format(row))
        cleared_lines += len(cleared_rows) + len(cleared_cols)
        clear_bonus = 0
        for x in range(len(cleared_rows) + len(cleared_cols)):
            clear_bonus += x + 1
        score += clear_bonus * 10
        move_num += 1
        # except InvalidMoveException:
        #     print("That is an invalid move, please make sure you are placing the piece in a valid space")
        # except:
        #     print("Please enter a valid piece number, enter the correct format for a move: piece_num, x, y")
        board.interact(win)
        if not board.current_pieces:
            board.refresh_pieces(win)
    
    win.erase()
    win.addstr(0, 0, "Perdi :(")
    win.refresh()
    win.raw_input()
    return move_num, cleared_lines, score, board, board.move_str
