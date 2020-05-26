import heapq
import random
import Boardgame_detector as bd
from colorama import init, Fore
from termcolor import colored
init()

# Cell and Astar Classes were used from the website:
# https://www.laurentluce.com/posts/solving-mazes-using-python-simple-recursivity-and-a-search/

class Cell(object):
    def __init__(self, x, y, reachable):
        """Initialize new cell.

        @param reachable is cell reachable? not a wall?
        @param x cell x coordinate
        @param y cell y coordinate
        @param g cost to move from the starting cell to this cell.
        @param h estimation of the cost to move from this cell
                 to the ending cell.
        @param f f = g + h
        """
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f


class AStar(object):
    def __init__(self):
        # open list
        self.opened = []
        heapq.heapify(self.opened)
        # visited cells list
        self.closed = set()
        # grid cells
        self.cells = []
        self.grid_height = None
        self.grid_width = None

    def init_grid(self, width, height, walls, start, end):
        """Prepare grid cells, walls.
        @param width grid's width.
        @param height grid's height.
        @param walls list of wall x,y tuples.
        @param start grid starting point x,y tuple.
        @param end grid ending point x,y tuple.
        """
        self.grid_height = height
        self.grid_width = width
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x, y) in walls:
                    reachable = False
                else:
                    reachable = True
                self.cells.append(Cell(x, y, reachable))
        self.start = self.get_cell(*start)
        self.end = self.get_cell(*end)

    def get_heuristic(self, cell):
        """Compute the heuristic value H for a cell.
        Distance between this cell and the ending cell multiply by 10.
        @returns heuristic value H
        """
        return 10 * (abs(cell.x - self.end.x) + abs(cell.y - self.end.y))

    def get_cell(self, x, y):
        """Returns a cell from the cells list.
        @param x cell x coordinate
        @param y cell y coordinate
        @returns cell
        """
        return self.cells[x * self.grid_height + y]

    def get_adjacent_cells(self, cell):
        """Returns adjacent cells to a cell.
        Clockwise starting from the one on the right.
        @param cell get adjacent cells for this cell
        @returns adjacent cells list.
        """
        cells = []
        if cell.x < self.grid_width-1:
            cells.append(self.get_cell(cell.x+1, cell.y))
        if cell.y > 0:
            cells.append(self.get_cell(cell.x, cell.y-1))
        if cell.x > 0:
            cells.append(self.get_cell(cell.x-1, cell.y))
        if cell.y < self.grid_height-1:
            cells.append(self.get_cell(cell.x, cell.y+1))
        return cells

    def get_path(self):
        cell = self.end
        path = [(cell.x, cell.y)]
        while cell.parent is not self.start:
            cell = cell.parent
            path.append((cell.x, cell.y))

        path.append((self.start.x, self.start.y))
        path.reverse()
        return path

    def update_cell(self, adj, cell):
        """Update adjacent cell.
        @param adj adjacent cell to current cell
        @param cell current cell being processed
        """
        adj.g = cell.g + 10
        adj.h = self.get_heuristic(adj)
        adj.parent = cell
        adj.f = adj.h + adj.g

    def solve(self):
        """Solve maze, find path to ending cell.
        @returns path or None if not found.
        """
        # add starting cell to open heap queue
        heapq.heappush(self.opened, (self.start.f, self.start))
        while len(self.opened):
            # pop cell from heap queue
            f, cell = heapq.heappop(self.opened)
            # add cell to closed list so we don't process it twice
            self.closed.add(cell)
            # if ending cell, return found path
            if cell is self.end:
                return self.get_path()
            # get adjacent cells for cell
            adj_cells = self.get_adjacent_cells(cell)
            for adj_cell in adj_cells:
                if adj_cell.reachable and adj_cell not in self.closed:
                    if (adj_cell.f, adj_cell) in self.opened:
                        # if adj cell in open list, check if current path is
                        # better than the one previously found
                        # for this adj cell.
                        if adj_cell.g > cell.g + 10:
                            self.update_cell(adj_cell, cell)
                    else:
                        self.update_cell(adj_cell, cell)
                        # add adj cell to open list
                        heapq.heappush(self.opened, (adj_cell.f, adj_cell))


# finds the exact cardinal location of a given player piece in the string itself
def get_location(rows, input_element):
    for i, row in enumerate(rows):
        for j, item in enumerate(row):
            if item == input_element:
                return j, i

# finds all available wall spaces and saves their cardinal coordinates in a list
def create_walls(rows, input_element):
    wall_list = []
    for i, row in enumerate(rows):
        for j, item in enumerate(row):
            if item == input_element:
                wall_list.append((j, i))
    return wall_list

# converts the board string into a manipulative list
def string_to_list(input_string):
    return [x.split('-') for x in input_string.split('\n')]


# converts a board list back into the original string
def list_to_string(input_list):
    return '\n'.join(['-'.join(x) for x in input_list])


count = 0

verticalStep = 58
horizontalStep = 2

exit_loc_x = 200
exit_loc_y = 200


# Uses the cardinal coordinate location of the character and returns its exact index in the string
def findPlayer(char):
    x, y = get_location(theList, char)
    playerIndex = ((y*12)+x)*2
    return playerIndex


# Moves the monster piece to the desired location that the Astar algorithm decided to move towards after 6 spaces
def moveMonster(moveList):
    global boardList

    x, y = moveList[len(moveList)-1]
    movementLocation = ((y*12)+x)*2
    positionM = findPlayer("M")

    boardList = boardList[:positionM] + 'o' + boardList[positionM+1:]
    boardList = boardList[:movementLocation] + 'M' + boardList[movementLocation+1:]

# Initializes the monster pieces position on the digital board 
# based on the current location of the piece on the physical board at the start of the game.
def moveMonsterStart(monster_x, monster_y):
    global boardList
    movementLocation = ((monster_y*12)+monster_x)*2
    positionM = findPlayer("M")

    boardList = boardList[:positionM] + 'o' + boardList[positionM+1:]
    boardList = boardList[:movementLocation] + 'M' + boardList[movementLocation+1:]

# Moves the human piece to the new position on the digital board based on 
# the change in position on the physical board
def moveHuman(human_x, human_y):
    movementLocation = ((human_y*12)+human_x)*2
    positionH = findPlayer("H")
    global boardList

    boardList = boardList[:positionH] + 'o' + boardList[positionH+1:]
    boardList = boardList[:movementLocation] + 'H' + boardList[movementLocation+1:]


boardList = """x-x-x-x-x-x-x-x-x-x-x-x
x-o-H-o-x-o-o-o-o-o-o-x
x-o-o-o-x-o-o-x-o-o-o-x
x-o-o-o-o-o-x-x-o-o-o-x
x-x-o-o-x-o-o-o-o-o-x-x
x-x-x-o-x-o-o-x-o-x-x-x
x-x-o-o-x-x-x-x-o-o-x-x
x-o-o-o-o-o-o-o-o-o-o-x
x-o-x-x-o-o-o-o-x-x-o-x
x-o-o-x-o-x-x-o-x-o-o-x
x-o-o-o-o-o-o-o-o-o-M-x
x-x-x-x-x-x-x-x-x-x-x-x"""

# Converts the above boardList into a string in-order to be further manipulated in the program
theList = string_to_list(boardList)



# Picks a randomly available space given the current board-state, and replaces that space with an 'E' denoting the boards Exit.
def generate_exit(rows, input_element):
    global boardList
    space_list = []
    for i, row in enumerate(rows):
        for j, item in enumerate(row):
            if item == input_element:
                space_list.append((j, i))
    exit_loc_x, exit_loc_y = random.choice(space_list)
    movementLocation = ((exit_loc_y*12)+exit_loc_x)*2
    boardList = boardList[:movementLocation] + 'E' + boardList[movementLocation+1:]
    return(exit_loc_x, exit_loc_y)

# created a temporary string in order to be manipulated to change each wall space to blue and to remove the '-' visually.
# The human and monster pieces are color changed as well respectively to yellow and blue on red.
def colorTheBoard():
    colorBoard = boardList
    colorBoard = colorBoard.replace('x', colored('x', 'blue', 'on_blue'))
    colorBoard = colorBoard.replace('H', colored('H', 'yellow', 'on_yellow'))
    colorBoard = colorBoard.replace('M', colored('M', 'blue', 'on_red'))
    colorBoard = colorBoard.replace('-', colored(''))
    print(colorBoard)


    
# function that converts the X and Y pixel positions on the webcam image into cardinal coordinates.
# Ex. (365, 82) would be converted to (2, 1)
# number conversation is based on a calibrated set of numbers available as monster_range_x and monster_range_y
def translatePosition(theName, coords):
    x_position, y_position = coords
    new_x = 0
    new_y = 0
    if(theName == "monster"):
        # possible values that X can be for the X coordinates
        # +-10 tolerance not applied
        monster_range_x = [314, 360, 398, 443, 490, 532, 574, 621, 661, 706]
        # possible values that Y can be for the Y coordinates
        # +-10 tolerance not applied
        monster_range_y = [81, 124, 165, 211, 251, 296, 345, 392, 431, 470]
        count = 1
        for x in monster_range_x:
            if(x_position > (x - 19) and x_position < (x + 19)):
                new_x = count
            count += 1
        count = 1
        for y in monster_range_y:
            if(y_position > (y - 19) and y_position < (y + 19)):
                new_y = count
            count += 1
        return new_x, new_y
    if(theName == "human"):
        # possible values that X can be for the X coordinates
        # +-10 tolerance not applied
        human_range_x = [327, 366, 406, 446, 494, 536, 574, 618, 662, 700]
        # possible values that Y can be for the Y coordinates
        # +-10 tolerance not applied
        human_range_y = [82, 124, 164, 212, 254, 296, 340, 386, 426, 468]
        count = 1
        for x in human_range_x:
            if(x_position > (x - 19) and x_position < (x + 19)):
                new_x = count
            count += 1
        count = 1
        for y in human_range_y:
            if(y_position > (y - 19) and y_position < (y + 19)):
                new_y = count
            count += 1
        return new_x, new_y

#turns webcam on for calibration of the pieces
bd.setup_video()

monster_start = 0
monster_end = 5
hasTreasure = False
foundTreasure = True
turn = 50

my_list = ["monster"]
the_dict = bd.send_coords(my_list)
k, v = next(iter(the_dict.items()))
newX, newY = translatePosition(k, v)
previous_x, previous_y = newX, newY
moveMonsterStart(previous_x, previous_y)

my_list = ["human"]
the_dict = bd.send_coords(my_list)
k, v = next(iter(the_dict.items()))
newX, newY = translatePosition(k, v)
previous_x, previous_y = newX, newY
moveHuman(previous_x, previous_y)

theList = string_to_list(boardList)

walls = create_walls(theList, "x")
start = get_location(theList, "M")
end = get_location(theList, "H")

theStar = AStar()

theStar.init_grid(12, 12, walls, start, end)

monsterPath = theStar.solve()
monsterMoves = monsterPath[:5]


while(turn != 0):

    colorTheBoard()
    
    # Checks if the turn is the humans turn, and waits for the player to physically move the piece
    # when the player types Q into the console it continues and moves the human piece on the board digitally
    if(turn % 2 == 0):
        print("It is the humans turn.")
        my_list = ["human"]
        
        # Uses object detection to find the current pixel position of the bounding box where the human piece is
        the_dict = bd.send_coords(my_list)
        k, v = next(iter(the_dict.items()))
        newX, newY = translatePosition(k, v)
        previous_x, previous_y = newX, newY
        moveHuman(previous_x, previous_y)
        
        prompt = input("Press Q to end turn:")
        
        # Moves the human piece based on the new detected position
        my_list = ["human", "treasure"]
        the_dict = bd.send_coords(my_list)
        
        for k, v in the_dict.items():
            # if human piece is detected, return the new X, Y coordinates
            if(k == "human"):
                newX, newY = translatePosition(k, v)
                
            # treasure piece is detected, sets the treasure boolean to true
            if(k == "treasure"):
                hasTreasure = True

        new_location_x, new_location_y = newX, newY

        global distance_moved
        distance_moved = (abs(new_location_x - previous_x) + abs(new_location_y - previous_y))
        my_list = ["human"]
        the_dict = bd.send_coords(my_list)
        k, v = next(iter(the_dict.items()))
        newX, newY = translatePosition(k, v)
        previous_x, previous_y = newX, newY
        moveHuman(previous_x, previous_y)
        
        # Checks if the player has found the treasure
        # if they have, sets the foundTreasure boolean to false so that the if statement is not triggered again
        if(hasTreasure is True and foundTreasure is True):
            print("YOU HAVE THE TREASURE, GET OUT")
            theList = string_to_list(boardList)
            exit_loc_x, exit_loc_y = generate_exit(theList, 'o')
            foundTreasure = False
        # Checks if the player's coordinates are the same as the exit coordinates,
        # which can only be possible if the treasure has been found
        if(previous_x == exit_loc_x and previous_y == exit_loc_y):
            print("YOU WON!!!!")
            break
        turn -= 1
    # Moves the monster digitally on the board if it is the monsters turn
    else:
        print("It is the monsters turn.")
        humanSneak = False
        theStar.opened = []
        heapq.heapify(theStar.opened)
        # visited cells list
        theStar.closed = set()
        # grid cells
        theStar.cells = []

        theList = string_to_list(boardList)
        # reinitializes human and monster position if the human did not sneak
        if(distance_moved > 2):
            start = get_location(theList, "M")
            end = get_location(theList, "H")
            
        # sets the sneak boolean to true if human piece moves 2 spaces or less
        if(distance_moved <= 2):
            humanSneak = True
        theStar.init_grid(12, 12, walls, start, end)
        monsterPath = theStar.solve()
        
        #  Forces the monster piece to continue following its path as long as the human piece is sneaking
        # by giving the monster piece the next five spaces in the full Astar path until it gets to the end
        if(humanSneak is True):
            monsterMoves = monsterPath[monster_start:monster_end]
            if(monster_end > len(monsterPath)):
                monster_end = len(monsterPath)
                monsterMoves = monsterPath[monster_start:monster_end]
        else:
            monsterMoves = monsterPath[0:5]
        moveMonster(monsterMoves)
        monster_start += 5
        monster_end += 5

        # Loss condition if the monster player kills the human player
        if('H' not in boardList):
            colorTheBoard()
            print("YOU LOST, MONSTER CAPTURED YOU")
            break

        my_list = ["monster"]
        the_dict = bd.send_coords(my_list)
        k, v = next(iter(the_dict.items()))
        newX, newY = translatePosition(k, v)
        turn -= 1
