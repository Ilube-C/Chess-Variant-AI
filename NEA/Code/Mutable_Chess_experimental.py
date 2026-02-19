#Mutable Chess 

#imports

import time

import pdb

import engine

import os #for loading rule sets from files

os.environ['SDL_VIDEO_CENTERED'] = '1' #centre pygame window

import pickle #for saving rule sets to files
import pygame #for playing and creating rule sets
import math #for calculating squaresize
import operator #used for repeated move calculation
import random #for Fishcer Random+
from copy import copy, deepcopy #for check and checkmate functions

import ctypes
ctypes.windll.user32.SetProcessDPIAware() #for getting the size of the user's monitor

#sound effect
pygame.mixer.init()
click = pygame.mixer.Sound(file = 'click.wav')

#colours

GREY = (200,200,200)
BLACK = (20,20,20)
GREEN = (50, 150, 50)
EMPTY = (0,0,0)

#positions

#generate alphabet
a = ord('a')
alph = [chr(i) for i in range(a,a+26)]

#will contain letters as keys with their corresponding index positions in the alphabet as values
chess_map_from_alpha_to_index = {}

#will contain numbers as keys with their corresponding letter with at that index value in the alphabet as values
chess_map_from_index_to_alpha = {}

def algebra_to_vector(pos):
        column = pos[0]
        row = pos[1:]
        row = int(row) - 1
        column = ord(column)-97
        coords = [column, row]
        return coords


def algebra_to_vector_2(pos):
        promotee = False
        if (pos[-1]).isalpha():
                promotee = pos[-1]
                #print(promotee)
                pos = pos[:-1]
                #print(pos)
        column = pos[0]
        row = pos[1:]
        row = int(row) - 1
        column = ord(column)-97
        coords = [column, row]
        
        return coords, promotee


        

def vector_to_algebra(coords):
        i = chr(coords[0]+97)
        j = str(coords[1] + 1)
        pos = i+j
        return pos

class GameBoard:

#Gameboard initialisation
    def __init__(self, agents, board, width, height, win_condition):
        self.agents = agents
        self.board = board
        self.w = width
        self.h = height
        self.wincon = win_condition
        self.create_notation() 

    def create_notation(self):
        for i in range(0, self.w):
            #uses width because number of columns is equal to width and rows dont use letters
            chess_map_from_alpha_to_index[alph[i]] = i
            chess_map_from_index_to_alpha[i] = alph[i]

#getter and setter for the board
    def getboard(self):
        return self.board

    def setboard(self, newboard):
        self.board = newboard

#draw board
    def draw_board(self, squaresize, w, h):
                
        width = w * squaresize
        height = h * squaresize

        size = (width, height)
        screen = pygame.display.set_mode(size)

        i = 1

        colours = [GREY, BLACK]

        #An offset is needed to ensure that the squares of the board alternate in colour
        if h%2 == 0:
            offset = True
        else:
            offset = False

        #drawing squares
        for c in range(w):
            if offset:
                i = i%2 + 1
            for r in range(h):
                pygame.draw.rect(screen, colours[i-1], (c*squaresize, r*squaresize, squaresize, squaresize))
                i = i%2 + 1

        #drawing pieces onto squares
        for c in range(w):
            for r in range(h):
                if type(self.board[r][c]) == str:
                     image = pygame.image.load('images\{}.png'.format(pieces[self.board[r][c]][0]))
                     image = pygame.transform.scale(image, (round(0.9*squaresize), round(0.9*squaresize)))
                     screen.blit(image, (c*squaresize+round(squaresize*0.05), r*squaresize+round(squaresize*0.05)))
                     
#play pre-amble

   

    def play(self):

            self.create_notation()

            pygame.init()

            end = False
            #game stops when this becomes true

            turn = 1
            #starts on turn 1

            touched = False
            #indicates whether a piece has been clicked on

            show_moves = False
            #indicates whether or not to display moves on the screen

            check = False
            #indicates whether or not a piece is in check

            previous_positions = []

            double_previous_positions = []

            if self.wincon == checkmate or self.wincon == KotH:
                    check_check = True
            else:
                    check_check = False

            #this variable is used as a parameter for the move generation function
            #it determines whether or not to factor in the laws of check when calculating moves


#dynamic squaresize
            squaresize = 0

            mon_width, mon_height = pygame.display.Info().current_w, pygame.display.Info().current_h

            while True:
                if squaresize * self.h < mon_height-100 and squaresize * self.w < mon_width-50:
                    squaresize+=1
                else:
                    break

#record game
            ans = input('Record game?:\n')

            if ans.lower() == 'yes':
                recording = True
                log = []
            else:
                recording = False
                
            white_depth = None
            black_depth = None
            
            ans1 = input("Make white player AI?\n")
            if ans1.lower() == 'yes':
                player = 'engine'
                while True:
                            try:
                                white_depth = int(input('engine depth(1-5):\n'))
                                if white_depth >= 1 and white_depth <= 5:
                                    break
                                else:
                                    print('Not within bounds')
                            except:
                                print('invalid input')  
                
            else:
                player = 'human'
                
            ans2 = input("Make black player AI?\n")
            if ans2.lower() == 'yes':
                opponent = 'engine'
                while True:
                            try:
                                black_depth = int(input('engine depth(1-5):\n'))
                                if black_depth >= 1 and black_depth <= 5:
                                    break
                                else:
                                    print('Not within bounds')
                            except:
                                print('invalid input')  
            else:
                opponent = 'human'
            
# play draw board

            printed_moves = False

            while True:

#win condition
                if not end: #once the game has ended, stops checking for win
                        if self.wincon == KotH:
                                end = self.wincon(self.board, self.w, self.h, turn, check, self.hills)
                                #the king of the hill win condition requires the hill squares to be passed as well as the normal variables
                        else:
                                end = self.wincon(self.board, self.w, self.h, turn, check)
                                #print(self.wincon(self.board, self.w, self.h, turn, check))

                if not end:
                    previous_positions, double_previous_positions, end = threefold_check(self.board, previous_positions, double_previous_positions)
                        #print("end in win condition section is {}".format(end))
                        #print(previous_positions, double_previous_positions)

#quit events
                if not end:
                    test_eng = engine.Engine(self.board, pieces)

                #AI turn
                if (turn == 1 and player == 'engine') or (turn == 2 and opponent == 'engine'):

                        depth = [white_depth, black_depth]

                        pygame.event.pump()

                        if not end:
                            self.draw_board(squaresize, self.w, self.h)
                            pygame.display.update()
                            self.board = test_eng.choose_move(self.board, depth[turn-1], turn) #depth
                            click.play()

                            #checks if a piece is in check
                            check = checkifcheck(self.board, turn, self.w, self.h)
                            #moves onto next turn
                            turn = next_turn(turn)

                #Human player turn or game end
                else:
                        #Draw board once before entering event loop
                        self.draw_board(squaresize, self.w, self.h)
                        if show_moves:
                            #if the last event was a piece being clicked, this statement displays all its legal moves
                            for i in legal_moves:
                                coords = algebra_to_vector(i)
                                screen.blit(image, (coords[0]*squaresize+round(squaresize/4), coords[1]*squaresize+round(squaresize/4)))
                        pygame.display.update()

                        loop = True
                        redraw = False
                        while loop:
                                if redraw:
                                    self.draw_board(squaresize, self.w, self.h)
                                    if show_moves:
                                        #if the last event was a piece being clicked, this statement displays all its legal moves
                                        for i in legal_moves:
                                            coords = algebra_to_vector(i)
                                            screen.blit(image, (coords[0]*squaresize+round(squaresize/4), coords[1]*squaresize+round(squaresize/4)))
                                    pygame.display.update()
                                    redraw = False

                                for event in pygame.event.get():
                                    #pygame.display.update()
                                    if end == True:
                                        if recording:
                                                print(log)
                                                recording = False
                                        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                                            pygame.display.quit()
                                            loop = False
                                            return
                                    
                                    if event.type == pygame.QUIT:
                                        pygame.display.quit()
                                        loop = False
                                        return

                                    if event.type == pygame.KEYDOWN:
                                        if event.key == pygame.K_ESCAPE:
                                            pygame.display.quit()
                                            loop = False
                                            return

                                    #pygame.display.update()
                                    
                                
                #show moves
                                    """      if show_moves:
                                            
                                    #if the last event was a piece being clicked, this statement displays all its legal moves 
                                        for i in legal_moves:
                                            coords = algebra_to_vector(i)
                                            screen.blit(image, (coords[0]*squaresize+round(squaresize/4), coords[1]*squaresize+round(squaresize/4)))
                                            #moves are represented by a red dot
                                            #pygame.display.update()"""

                #mouse clicks
                                    if event.type == pygame.MOUSEBUTTONDOWN:
                                        x, y = event.pos
                                        column = int(math.floor(x/squaresize))
                                        row = int(math.floor(y/squaresize))
                                        #works out column and row based on x and y co-ordinate of mouse press
                                        coords = column, row
                                        pos = vector_to_algebra(coords)
                                        #pos is the square thats been clicked on
                                        choice = self.board[row][column]
                                        #choice is the object on the square thats been clicked on

                #if a piece has been selected
                                        if type(touched) == str:
                                        #if a piece was touched last event...
                                            if pos in legal_moves:
                                            #and if a legal move for that piece was touched this event..
                                                #square that the piece was on is made empty
                                                self.board[last_row][last_column] = 1
                                                #contents of target square are recorded for the game log
                                                target = self.board[row][column]
                                                click.play()
                                                if target != 1:
                                                        previous_positions = []
                                                        double_previous_positions = []
                                                #target square is populated with chosen piece
                                                self.board[row][column] = touched
                                                legal_moves = []
                                                show_moves = False
                                                #a move is made
                                                printed_moves = False
                                                redraw = True


                #updates game info
                                                #promotes any unpormoted piece
                                                self.board, promotee = promotion_check(self.board, self.h, self.agents, player, opponent, pieces)
                                                #checks if a piece is in check
                                                check = checkifcheck(self.board, turn, self.w, self.h)
                                                #moves onto next turn
                                                turn = next_turn(turn) 
                                                #pygame.display.update()
                                                loop = False

                                                #if the user requested to record the game, logs the move that has just occurred
                                                if recording:
                                                    if promotee:
                                                            previous_positions = []
                                                            double_previous_positions = []
                                                            log.append('{}:{} ({})'.format(vector_to_algebra([last_column,last_row]),pos,promotee))
                                                    else:
                                                            log.append('{}:{}'.format(vector_to_algebra([last_column,last_row]),pos))

                                                #lets go of the piece that was touched last event
                                                touched = False

                                            else:
                                                legal_moves = []
                                                #lets go of the piece that was touched last event
                                                touched = False
                                                show_moves = False
                                                redraw = True
                                                #pygame.display.update()
                                                
                #if a piece hasn't been selected
                                        else:
                                            #if an empty square or wall is clicked, nothing happens
                                            if choice == 1 or choice == 4:
                                                    pass
                                            #checks if its that players turn
                                            elif choice.isupper() ^ turn-1:
                                                    #calculates that piece's moves
                                                    legal_moves = (pieces[choice])[1].getMoves(pos, self.board, turn, check_check, self.w, self.h)
                                                    if legal_moves:
                                                        touched = choice
                                                        #saves previous position for use in next loop
                                                        last_column = column
                                                        last_row = row
                                                        #loads the image of the red dot for use in next loop 
                                                        image = pygame.image.load('images\\red_dot.png')
                                                        image = pygame.transform.scale(image, (round(0.5*squaresize), round(0.5*squaresize)))
                                                        width = self.w * squaresize
                                                        height = self.h * squaresize
                                                        size = (width, height)
                                                        screen = pygame.display.set_mode(size)

                                                        show_moves = True
                                                        redraw = True

                                            #if an enemy piece is clicked
                                            else:
                                                print('enemy piece\n')


#custom board class
class CustomGameBoard(GameBoard): #Class used to create user customised game boards

    #custom game board initialisation
    def __init__(self, agents, fairies, board, width, height, win_condition):
        #fairy pieces specific to this ruleset
        self.fairies = fairies
        self.hills = []
        #parent initialisation function
        super().__init__(agents, board, width, height, win_condition)
        #board deesign
        if board != defaultBoard:
            self.creation()

#getter for faries
    def getfairies(self):
        return self.fairies

#getter and setter for hills
    def gethills(self):
        return self.hills

    def sethills(self, newhills):
        self.hills = newhills

#custom draw board function
    #function to draw board with pygame graphics
    def draw_board(self, squaresize, w, h): #different squaresize for design and play 
                                            #width and heigh must be specified becuase different values are used for design and play
    
        width = w * squaresize
        height = h * squaresize

        size = (width, height)
        screen = pygame.display.set_mode(size)

        i = 1

        colours = [GREY, BLACK]

        #An offset is needed to ensure that the squares of the board alternate in colour
        if h%2 == 0:
            offset = True
        else:
            offset = False

        for c in range(w):
            if offset:
                i = i%2 + 1
            for r in range(h):
                pygame.draw.rect(screen, colours[i-1], (c*squaresize, r*squaresize, squaresize, squaresize))
                i = i%2 + 1
                
        for i in self.hills: 
            pygame.draw.rect(screen, GREEN, (i[1]*squaresize+round(squaresize*0.1), i[0]*squaresize+round(squaresize*0.1), 0.8*squaresize, 0.8*squaresize))
     
        for c in range(w):
            for r in range(h):
                if type(self.board[r][c]) == str:
                     image = pygame.image.load('images\{}.png'.format(pieces[self.board[r][c]][0]))
                     image = pygame.transform.scale(image, (round(0.9*squaresize), round(0.9*squaresize)))
                     screen.blit(image, (c*squaresize+round(squaresize*0.05), r*squaresize+round(squaresize*0.05)))
                if self.board[r][c] == 2:
                     pygame.draw.rect(screen, EMPTY, (c*squaresize, r*squaresize, squaresize, squaresize))
                if self.board[r][c] == 3:
                     image = pygame.image.load('images\\tick.png')
                     image = pygame.transform.scale(image, (round(0.9*squaresize), round(0.9*squaresize)))
                     screen.blit(image, (c*squaresize+round(squaresize*0.05), r*squaresize+round(squaresize*0.05)))
                if self.board[r][c] == 4:
                     image = pygame.image.load('images\wall.png')
                     image = pygame.transform.scale(image, (round(0.9*squaresize), round(0.9*squaresize)))
                     screen.blit(image, (c*squaresize+round(squaresize*0.05), r*squaresize+round(squaresize*0.05)))
                if self.board[r][c] == 5:
                     image = pygame.image.load('images\hill.png')
                     image = pygame.transform.scale(image, (round(0.9*squaresize), round(0.9*squaresize)))
                     screen.blit(image, (c*squaresize+round(squaresize*0.05), r*squaresize+round(squaresize*0.05)))
                     #this represents a hill marker which tells the creation function where hills should be placed
        
#function in which the user designs board
    def creation(self):

#creation board construction

        pygame.init()

        #function to work out extra height
        extra_h = extra_row_count(self.w, 1, self.agents)

        squaresize = 0

        mon_width, mon_height = pygame.display.Info().current_w, pygame.display.Info().current_h


        while True:
            if squaresize * (self.h+extra_h+1) < mon_height-100 and squaresize * self.w < mon_width-50:
                squaresize+=1
            else:
                break
        
#Creation function pre-amble

        piece = False
        #whether a piece is held
        
        while True:
                

                playable = False
                #is the gamemode playable yet

                white = False
                #are there white pieces

                black = False
                #are there black pieces
                
                white_royal = False
                #are there royal white pieces

                black_royal = False
                #are there royal black pieces

                hill = False
                #are there any hill squares

#checks playability
                for y in range(self.h):
                    for x in range(self.w):
                        if type(self.board[y][x]) == str and self.board[y][x].isupper():
                            white = True
                            if pieces[self.board[y][x]][1].getStatus() == 'royal':
                                white_royal = True
                #checks board for white pieces
                        
                for y in range(self.h):
                    for x in range(self.w):
                        if type(self.board[y][x]) == str and self.board[y][x].islower():
                            black = True
                            if pieces[self.board[y][x]][1].getStatus() == 'royal':
                                    black_royal = True
                #checks board for black pieces

                for y in range(self.h):
                    for x in range(self.w):
                        if self.board[y][x] == 5:
                                    hill = True
                #checks if the user has set any hills

                if self.wincon == extinction:
                    if white and black:
                        playable = True
                
                        
                if self.wincon == checkmate or self.wincon == regicide:
                    if white_royal and black_royal:
                                playable = True

                if self.wincon == KotH:
                    if white_royal and black_royal and hill:
                                playable = True
                #checks if the game is playable, different for each win condition

                for y in range(self.h):
                    for x in range(self.w):
                        if type(self.board[y][x]) == str and pieces[self.board[y][x]][1].getStatus() == 'royal':
                                if checkifcheck(self.board[:self.h], 1, self.w, self.h) or checkifcheck(self.board[:self.h], 2, self.w, self.h):
                                        playable = False
                #if a piece starts in check the board state is not playable

#event loop                
                self.draw_board(squaresize, self.w, self.h+extra_h+1)


                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.display.quit()
                        self.board = []
                        #if the user quits, the board isn't defined
                        return
                        
                    pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    column = int(math.floor(x/squaresize))
                    row = int(math.floor(y/squaresize))
                    coords = column, row
                    pos = vector_to_algebra(coords)
                    
                    choice = board[row][column]

                    if choice in self.agents:
                    #if a board object has been chosen
                        if row > self.h:
                        #if the chosen object is below the separation line (in the creative tools)
                            piece = choice
                            #turns the held piece to that object
                        else:
                        #if its above
                            self.board[row][column] = 1
                            #removes the object

                    elif choice == 1:
                    #if an empty square is chosen
                        if piece and row < self.h:
                        #if a piece has been selected and the square chosen is on the board
                            self.board[row][column] = piece
                            #places piece there

                    elif choice == 2:
                        pass
                    #if an empty square is clicked, does nothing

                    elif choice == 3:
                    #if the tick button was pressed
                        if playable:
                            for y in range(self.h):
                                for x in range(self.w):
                                    if self.board[y][x] == 5:
                                        self.board[y][x] = 1
                                        self.hills.append((y, x))
                                        #iterates through board and adds any hills found to the hills array
                            self.board = self.board[:self.h]
                            #sets the game board to be just the board component of the creation board.
                            pygame.display.quit()
                            return

                        else:
                                print('not playable') 
                                

                pygame.display.update

#default board

defaultBoard = [['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
              ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
              [  1,   1,   1,   1,   1,   1,   1,   1],
              [  1,   1,   1,   1,   1,   1,   1,   1],
              [  1,   1,   1,   1,   1,   1,   1,   1],
              [  1,   1,   1,   1,   1,   1,   1,   1],
              ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
              ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']]

#piece class initialisation
class Piece:

    def __init__(self, letter, sprite, vectors_ride = None, vectors_leap = None):
        self.letter = letter
        #unique identifier
        self.sprite = sprite
        self.vec_ride = vectors_ride
        self.vec_leap = vectors_leap

    def getStatus(self):
        return 'common'

#get moves

    def getMoves(self, pos, board, turn, check_check, w, h):
        #print(self.letter)
        coords = algebra_to_vector(pos)
        #piece's location
        column, row = coords
        #will continue to represent the piece's location
        operators = [operator.add, operator.sub]
        moves = []

#leaps
        if self.vec_leap:

            for v in self.vec_leap:
                    if v[1] == v[0]:
                           for f in operators:
                                for g in operators:
                                        moves += leap_move(f, g, v[0], v[1], board, self.letter, column, row)
                    elif v[0] == 0:
                            g = operators[0]
                            for f in operators:
                                    moves += leap_move(g, f, v[0], v[1], board, self.letter, column, row)
                                    moves += leap_move(f, g, v[1], v[0], board, self.letter, column, row)
                    elif v[1] == 0:
                            g = operators[0]
                            for f in operators:
                                    moves += leap_move(f, g, v[0], v[1], board, self.letter, column, row)
                                    moves += leap_move(g, f, v[1], v[0], board, self.letter, column, row)
                                            
                    else:
                        for f in operators:
                                for g in operators:
                                        moves += leap_move(f, g, v[0], v[1], board, self.letter, column, row)
                                        moves += leap_move(f, g, v[1], v[0], board, self.letter, column, row)
                                
#rides
        if self.vec_ride:
                
                for v in self.vec_ride:
                    if v[1] == v[0]:
                           for f in operators:
                                for g in operators:
                                        moves += ride_move(f, g, v[0], v[1], board, self.letter, column, row)
                    elif v[0] == 0:
                            g = operators[0]
                            for f in operators:
                                    moves += ride_move(g, f, v[0], v[1], board, self.letter, column, row)
                                    moves += ride_move(f, g, v[1], v[0], board, self.letter, column, row)
                    elif v[1] == 0:
                            g = operators[0]
                            for f in operators:
                                    moves += ride_move(f, g, v[0], v[1], board, self.letter, column, row)
                                    moves += ride_move(g, f, v[1], v[0], board, self.letter, column, row)
                                    
                            
                    else:
                        for f in operators:
                                for g in operators:
                                        moves += ride_move(f, g, v[0], v[1], board, self.letter, column, row)
                                        moves += ride_move(f, g, v[1], v[0], board, self.letter, column, row)
                                
#Filter all negative values

        temp = [i for i in moves if i[0] >=0 and i[1] >=0]
        
        allPossibleMoves = []

        for i in temp:
                allPossibleMoves.append(vector_to_algebra(i))

#check for check       
        if check_check:
        #if the laws of check are being considered
            royal_moves = []

            for i in allPossibleMoves:
                newpos = algebra_to_vector(i)
                #print(board)
                if not royal_attacked(board, self.letter, turn, newpos, coords, w, h):
                #filters all moves that result in a royal piece being attacked
                    royal_moves.append(i)

            allPossibleMoves = royal_moves

            
        allPossibleMoves = list(dict.fromkeys(allPossibleMoves))
        return allPossibleMoves

#Pawn Class
class Pawn(Piece):

        def getStatus(self):
                return 'pawn'

        def getMoves(self, pos, board, turn, check_check, w, h):
                #print(self.letter)
                coords = algebra_to_vector(pos)
                j, i = coords
                column, row = coords
                moves = []

                #white pawn
                if self.letter.isupper():
                    try:
                        temp = board[i+1][column]
                        if temp == 1:   #checks if the square is empty
                            moves.append((column,i+1))
                    except:
                        pass

                    if row == 1:
                        temp = board[i+1][column]
                        temp2 = board[i+2][column]#checks if both squares are empty
                        if temp == 1 and temp2 == 1:  
                            moves.append((column,i+2))

                    try:
                        temp = board[i+1][j+1] #diagonal capture
                        if temp.lower() == temp:
                            moves.append((j+1,i+1))
                    except:
                        pass

                    try:
                        temp = board[i+1][j-1]
                        if temp.lower() == temp:
                            moves.append((j-1,i+1))
                    except:

                        pass

                #black pawn
                if self.letter.islower(): #same as above but in opposite direction
                    if i > 0:
                        try:
                            temp = board[i-1][column]
                            if temp == 1:   
                                moves.append((column,i-1))
                        except:
                            pass

                    if row == (h-2):
                        temp = board[i-2][column]
                        temp2 = board[i-1][column]
                        if temp == 1 and temp2 == 1:  
                            moves.append((column,i-2))

                    try:
                        temp = board[i-1][j+1]
                        if temp.upper() == temp:
                            moves.append((j+1,i-1))
                    except:
                        pass

                    try:
                        temp = board[i-1][j-1]
                        if temp.upper() == temp:
                            moves.append((j-1,i-1))
                    except:
                        pass

                #Filter all negative values

                temp = [i for i in moves if i[0] >=0 and i[1] >=0]
                
                allPossibleMoves = []

                for i in temp:
                        allPossibleMoves.append(vector_to_algebra(i))

                #check for check       
                if check_check:
                #if the laws of check are being considered
                    royal_moves = []

                    for i in allPossibleMoves:
                        newpos = algebra_to_vector(i)
                        #print(board)
                        if not royal_attacked(board, self.letter, turn, newpos, coords, w, h):
                        #filters all moves that result in a royal piece being attacked
                            royal_moves.append(i)

                    allPossibleMoves = royal_moves
 
                return allPossibleMoves
        
#royal piece
class Royal(Piece):
        def getStatus(self):
                return 'royal'
   
#standard pieces
#(self, letter, vectors_ride = None, vectors_leap = None)
white_pawn = Pawn('P', 'white_pawn')
white_rook = Piece('R', 'white_rook', [[0,1]])
white_knight = Piece('N', 'white_knight', None, [[1,2]])
white_bishop = Piece('B', 'white_bishop', [[1,1]])
white_king = Royal('K', 'white_king', None, [[0,1],[1,1]])
white_queen = Piece('Q', 'white_queen', [[0,1],[1,1]])
black_pawn = Pawn('p', 'black_pawn')
black_rook = Piece('r', 'black_rook', [[0,1]])
black_knight = Piece('n', 'black_knight', None, [[1,2]])
black_bishop = Piece('b', 'black_bishop', [[1,1]])
black_king = Royal('k', 'black_king', None, [[0,1],[1,1]])
black_queen = Piece('q', 'black_queen', [[0,1],[1,1]])

fairies = []


letters = ['a','c','d','e','f','g','h','i','j','l','m','o','s','t','u','v','w','x', 'y', 'z']
#unique identifiers

sprites = ['elephant', 'princess', 'prince'] 

#pieces
pieces = {
          'P':['white_pawn',white_pawn],
          'R':['white_rook',white_rook],
          'N':['white_knight',white_knight],
          'B':['white_bishop',white_bishop],
          'K':['white_king',white_king],
          'Q':['white_queen',white_queen],
          'p':['black_pawn',black_pawn],
          'r':['black_rook',black_rook],
          'b':['black_bishop',black_bishop],
          'n':['black_knight',black_knight],
          'k':['black_king',black_king],
          'q':['black_queen',black_queen]
          }

#dictionary containing pieces and their image file

#next turn
def next_turn(turn):
        turn = turn%2+1
        return turn

#leap moves
def leap_move(f, g, m, n, board, piece, column, row):
        
        moves = []
        try:
                temp = board[f(row, m)][g(column, n)]
                #tests if a square is on the board
                if temp == 1 or (temp.isupper() ^ piece.isupper()):
                #if square is empty or contains enemy piece
                        moves = [[g(column, n), f(row, m)]]
        except:
                pass
        return moves

#ride moves
def ride_move(f, g, m, n, board, piece, column, row):
        moves = []
        i = 1
        while True:
                try:
                        temp = board[f(row,(m*i))][g(column,(n*i))]
                        #tests if a square is on the board
                except:
                        break
                        #if not, stops calculating moves in that direction
                if temp == 1:
                        moves+=[[g(column,(n*i)), f(row,(m*i))]]
                        #if a square is empty adds it to possible moves
                        i+=1
                elif temp == 4:
                        break
                        #if a wall is hit, stops calculating moves in that direction
                elif temp.isupper() ^ piece.isupper():
                        moves+=[[g(column,(n*i)), f(row,(m*i))]]
                        #if an enemy piece is hit, adds its locations to possible moves then stops calculating moves in that direction
                        break
                else:
                        break
                        #this case only occurs when a friendly piece is hit, in which case it stops calculating moves in that direction
        return moves

#extra row count
def extra_row_count(width, count, agents):
        #count starts at 1

    if int(width)*int(count) >= len(agents):
    #multiplies the width of the board by the count of extra rows to see if it can contain all the creation tools
        return count
        #base case
        #if it fits all the pieces, the count is returned

    else:
        return extra_row_count(width, count+1, agents)
        #general case
        #if not, it increases the count and performs the function again

#promotion
def promotion_check(chessBoard, h, agents_, player, opponent, pieces, promotee = None):
        

    #print(pieces) 
    agents = []
    choice = False

    for i in agents_:
            if type(i) == str and i.lower() != 'p' and pieces[i][1].getStatus() != 'royal':
                    agents.append(i)
        #selects only the non-pawn pieces to be promoted 

   

    for i in range(len(chessBoard[0])):
        if chessBoard[0][i] == 'p':
        #black pawn 
            
            if opponent == 'engine':
                    #choices = [piece for piece in agents if piece.islower()]
                    choice = promotee
            else:
                    while True:
                        for p in agents:
                                if p.islower():
                                        print(p)
                        choice = input('Select a piece to promote to...\n')
                        if choice in agents and choice.islower():
                            break
                        else:
                            print('Invalid answer') 
            chessBoard[0][i] = choice
            
    for i in range(len(chessBoard[h-1])): 
        if chessBoard[h-1][i] == 'P':
        #white pawn
            
            if player == 'engine':
                    #choices = [piece for piece in agents if piece.isupper()]
                    choice = promotee
            else:
                    while True:
                        for p in agents:
                                if p.isupper():
                                        print(p)
                        choice = input('Select a piece to promote to...\n')
                        if choice in agents and choice.isupper():
                            break
                        else:
                            print('Invalid answer') 
            chessBoard[h-1][i] = choice

    return chessBoard, choice


#function to check for check
def checkifcheck(board, turn, w, h):

    chessBoard = deepcopy(board)
    #creates deepcopy of the board

    attacked_spaces = [] 

    moves = []

    for x in range(h):
        for y in range(w):
            if chessBoard[x][y] == 5:
                chessBoard[x][y] = 1
    #replaces all hills markers with empty squares
    
    for x in range(h):
        for y in range(w):
                if (type(chessBoard[x][y]) == str)  and (((chessBoard[x][y]).islower()) == turn-1):
                #finds every piece belonging to the attacking player
                        moves.append(pieces[chessBoard[x][y]][1].getMoves((chr(y+97)+str(x+1)), chessBoard, turn-1, False, w, h))

    for z in moves:
        if z:
            for q in z:
                if q not in attacked_spaces:
                    attacked_spaces.append(q)
                    #filters all squares that are attacked twice

    #print(attacked_spaces) 
    for i in attacked_spaces:
        y = algebra_to_vector(i)
        if chessBoard[y[1]][y[0]] != 1:
            if pieces[chessBoard[y[1]][y[0]]][1].getStatus() == 'royal':
               return True
        #if one of these squares contains a royal piece, then there is check

    return False

#function to see if a royal piece is being attacked after a move is made
def royal_attacked(chessBoard, piece, turn, newpos, origpos, w, h):
    #is passed all the infor about the board as well as the info about the move being tested for legality

    moves = []
    attacked_spaces = []

    tempBoard = deepcopy(chessBoard)
    #creates a deep copy of the board
    
    tempBoard[origpos[1]][origpos[0]] = 1
    tempBoard[newpos[1]][newpos[0]] = piece
    #makes the move about to be made
    
    return checkifcheck(tempBoard, next_turn(turn), w, h)
    #sees if the move has resulted in a check

#win conditions

#extinction
def extinction(board, w, h, turn, check = None, hills = None):
        white_exists = False

        black_exists = False

        #assumes no pieces exist

                        
        for y in range(h):
                for x in range(w):
                        if type(board[y][x]) == str and board[y][x].isupper():
                                white_exists = True
                        if type(board[y][x]) == str and board[y][x].islower():
                                black_exists = True
        #checks each side for a piece
                                            
        if not white_exists:
                pygame.display.update()
                print('==========\n\nBlack wins\n\n===========\n')
                return True

        if not black_exists:
                pygame.display.update()
                print('==========\n\nWhite wins\n\n===========\n')
                return True
        #if either side has no pieces, game ends
        
        return False
        #otherwise game continues

#checkmate
def checkmate(board, w, h, turn, check, hills = None):

       
        check_check = True
        allowed_moves = []
                            
        #calculate every move of current player
        for x in range(h):
                for y in range(w):
                        if type(board[x][y]) == str  and (board[x][y]).isupper() ^ turn-1:
                                move = (pieces[board[x][y]][1].getMoves((chr(y+97)+str(x+1)), board, turn, True, w, h))

                                if move:
                                        allowed_moves.append(move)
                                        

        #if there are no moves, the game ends
        if not allowed_moves:           
                if check == True:
                #if a royal is in check then it is a checkmate
                        if turn == 1:
                                pygame.display.update()
                                print('==========\n\nBlack wins\n\n===========\n')
                                return True
                                    
                        elif turn == 2:
                                pygame.display.update()
                                print('==========\n\nWhite wins\n\n===========\n')
                                return True
                else:
                #if no piece is in check then it is a stalemate
                                    pygame.display.update()
                                    print('==========\n\nStalemate\n\n===========\n')
                                    return True

        return False
        #if the player can still make a move, the game continues

#king of the hill
def KotH(board, w, h, turn, check, hills):
        if checkmate(board, w, h, turn, check):
                return True

        if hills:
                for i in hills:
                                if type(board[i[0]][i[1]]) == str and pieces[board[i[0]][i[1]]][1].getStatus() == 'royal' and board[i[0]][i[1]].isupper():
                                        pygame.display.update()
                                        print('==========\n\nWhite wins\n\n===========\n')
                                        return True
                                                    
                                if type(board[i[0]][i[1]]) == str and pieces[board[i[0]][i[1]]][1].getStatus() == 'royal' and board[i[0]][i[1]].islower():
                                        pygame.display.update()
                                        print('==========\n\nBlack wins\n\n===========\n')
                                        return True
                                #if a royal is on a hill, game ends
        return False
        
#regicide        
def regicide(board, w, h, turn, check = None, hills = None):

        white_royals = False

        black_royals = False
                        
        for y in range(h):
                for x in range(w):
                        if type(board[y][x]) == str and board[y][x].isupper():
                                if pieces[board[y][x]][1].getStatus() == 'royal':
                                        white_royals = True


        for y in range(h):
                for x in range(w):
                        if type(board[y][x]) == str and board[y][x].islower():
                                if pieces[board[y][x]][1].getStatus() == 'royal':
                                        black_royals = True
        #searches for royal pieces

        if not white_royals:
                pygame.display.update()
                print('==========\n\nBlack wins\n\n===========\n')
                return True

        if not black_royals:
                pygame.display.update()
                print('==========\n\nWhite wins\n\n===========\n')
                return True
        #if a side lacks a royal piece, game ends

        return False

#Threefold repetition check
def threefold_check(new_board, previous_positions, double_previous_positions):

        end_ = False
        
        if new_board in double_previous_positions:
                print('==========\n\nThree Fold Repetition\n\n===========\n')
                end_ = True

        elif new_board in previous_positions:
                double_previous_positions.append(deepcopy(new_board))

        else:
                previous_positions.append(deepcopy(new_board))

        return previous_positions, double_previous_positions, end_


#50 move rule check
        
#prompt
if __name__ == '__main__':

    mainloop = True

    while mainloop:

        try:
            choice = input('1:play default\n2:play Fischer Random+\n3:create ruleset\n4:delete ruleset\n5:play custom\n')
            #user is propmpted
            if choice.lower() == 'quit':
                mainloop = False
            #quit option
            elif choice.lower() == 'help':
            #help menu
                print('\n\nNaviagting the program:\nWhen given items listed numerically, type in the number of the item you wish to select\nWhen asked a binary question type \'yes\' to confirm or enter anything else to deny\n')
                print('Pieces:')
                print('Piece movement is represented by 2-dimensional vectors. These can be interpreted in two ways:\n1:As a leaping vector, in which case the piece can move once by that vector in all directions\n2:As a riding vector, in which case the piece can move infinitely by that vector until it is blocked.\n(so a knight is a [1,2] leaper and a bishop is a [1,1] rider')
                print('A piece\'s status can either be common or royal. The properties of royal pieces are dependent on the game\'s win condition\n')
                print('Win conditions:\n1:Checkmate: the standard rules of Chess, games can result in checkmate on any royal piece for either side or stalemate\n2:Regicide: the laws of check do not apply, if an enemy royal is captured, the game is won\n3:King of the Hill: Same as the Checkmate but with hill squares which give victory to a player that moves their royal piece onto the hill.\n4:Extinction: The laws of check do not apply, all enemy pieces must be captured to win.')
                print('Custom rulesets are not playable unless there are sufficient pieces for the win condition to be achieved.\n')
            else:
                choice = int(choice)
                
        except:
            choice = 0
            #if choice is invalid, sets it to 0 for error handling clause

#default       
        if choice == 1:
            agents = [4,'P','R','N','B','K','Q','p','r','n','b','k','q']
            ChessBoard = GameBoard(agents, deepcopy(defaultBoard), 8, 8, checkmate)
            #default rules
            ChessBoard.play()

#Fischer random+
        elif choice == 2:
            agents = [4,'P','R','N','B','K','Q','p','r','n','b','k','q']

            while True:
                try:
                    w = int(input('Width of the board(4-26):\n'))
                    if w < 27 and w > 3:
                        break
                    else:
                        print('Not within bounds')
                except:
                    print('invalid input') 
                                    
                
            while True:
                try:
                    h = int(input('Height of the board(4-26):\n'))
                    if h < 27 and h > 3:
                        break
                    else:
                        print('Not within bounds')
                except:
                    print('invalid input')

            #gets height and width of the board

            random_pieces = []
            
            for i in (agents):
                if type(i) is str and i == i.lower() and i.lower() != 'k' and i.lower() != 'p':
                    random_pieces.append(i)
            #adds all the white pieces to a list 

            board = [[1] * w for i in range(h)]
            #creates a board of the dimensions specified by the user

            white_pawns = []
            for i in range(w):
                 white_pawns.append('P')
            board[1] = white_pawns

            black_pawns = []
            for i in range(w):
                 black_pawns.append('p')
            board[h-2] = black_pawns
            #fills the second and penultimate rows with pawns

            for i in range(w):
               x = random.choice(random_pieces)
               board[0][i] = x.upper()
               board[h-1][i] = x
               #chooses a random piece and adds a white one to the white side and black on to the blakc side
               
            kingspot = random.randint(0,i)

            board[0][kingspot] = 'K'

            board[h-1][kingspot] = 'k'
            #randomly places the kings

            ChessBoard = GameBoard(agents, board, w, h, checkmate)
            ChessBoard.play()
            #defines the game and starts playing

#custom ruleset
        elif choice == 3:
                
            agents = [4,'P','R','N','B','K','Q','p','r','n','b','k','q']
            
            print(len(sprites))
            while len(sprites) > 0:
                ans = input('Would you like to make a new piece?({} more possible):\n'.format(len(sprites)))
                #the user is asked to make a custom piece up to 3 times

                if ans.lower() == 'yes':
                        #name = input('Choose a name for the piece:\n').lower()
                            
                    
                        
                        while True:
                                letter = input('Choose a letter to represent the piece:\n').lower()
                                if letter in letters:
                                        break
                                else:
                                        print('not a valid letter choice')

                        sprite = False
                        while not sprite:
                                print('Select one from the following:\n')
                                for i in range(len(sprites)):
                                        print('{}:{}'.format(i+1, sprites[i]))
                                        
                                while True:
                                        
                                        try:
                                                
                                                choice = int(input(''))
                                                if choice > 0 and choice <= len(sprites):
                                                        break
                                                else:
                                                        print('Not an option')
                                        except:
                                            print('Invalid input')

                                sprite = sprites[choice-1]
                                #print(sprite)
                                sprites.remove(sprite)
                                print(len(sprites))

                        vec_ride = []
                        vec_leap = []

                        while True:
                                ans = input('Add rides?\n')
                                if ans.lower() != 'yes':
                                        break

                                #can't use while not m/n because m/n might be set to 0

                                m = False
                                while not type(m) is int:
                                        try:
                                                m = int(input('First dimension?\n'))
                                        except:
                                                print('answer must be an integer')
                                    
                                
                                n = False
                                while not type(n) is int:
                                        try:
                                                n = int(input('Second dimension?\n'))
                                        except:
                                                print('answer must be an integer')


                                        vec_ride.append([m,n])


                        while True:
                                ans = input('Add leaps?\n')
                                if ans.lower() != 'yes':
                                    break

                                m = False
                                while not type(m) is int:
                                    try:
                                        m = int(input('First dimension?\n'))
                                    except:
                                        print('answer must be an integer')
                                    
                                
                                n = False
                                while not type(n) is int:
                                    try:
                                        n = int(input('Second dimension?\n'))
                                    except:
                                        print('answer must be an integer')

                                vec_leap.append([m,n])
                            #rides and leaps are inputed by the user

                
                        ans = input('Is the piece royal?:\n')
                        if ans.lower() == 'yes':
                                define = Royal
                        else:
                                define = Piece

                        if not vec_ride and not vec_leap and define == Piece:
                                print('no piece created.')
                                
                        else:
                                pieces[letter.upper()] = ['white_'+sprite, define(letter.upper(),'white_'+sprite, vec_ride, vec_leap)]

                                pieces[letter] = ['black_'+sprite, define(letter,'black_'+sprite, vec_ride, vec_leap)]
                                
                                agents += [letter, letter.upper()]

                                fairies.append([define(letter.upper(), 'white_'+sprite, vec_ride, vec_leap), define(letter, 'black_'+sprite, vec_ride, vec_leap)])

                else:
                        sprites = [] 

                win_condition = False

#win condition choice                
            while not win_condition:
                try:
                    ans = int(input('Select a win condition\n1:Checkmate\n2:Regicide\n3:King of the Hill\n4:Extinction\n'))
                except:
                    ans = 0
                    
                
                
                if ans == 1:
                        win_condition = checkmate
                elif ans == 2:
                        win_condition = regicide
                elif ans == 3:
                        agents = [5] + agents
                        win_condition = KotH
                elif ans == 4:
                        win_condition = extinction
                        
                else:
                    print('Invalid answer') 

            ChessBoard = False

            while not ChessBoard:
                try:
                    ans = int(input('1:Default Board\n2:Custom Board\n'))
                except:
                    ans = 0

                if ans == 1:
                        board = deepcopy(defaultBoard)
                        
                        TempBoard = CustomGameBoard(agents, fairies, board, 8, 8, win_condition)
                        if win_condition == KotH:
                            TempBoard.sethills([[3, 3], [3, 4], [4, 3], [4, 4]])
                            #if default board is selected with king of the hill, central four squares become hills
                        ChessBoard = TempBoard

                elif ans == 2:
                    while True:
                            try:
                                w = int(input('Width of the board(2-26):\n'))
                                if w < 27 and w > 1:
                                    break
                                else:
                                    print('Not within bounds')
                            except:
                                print('invalid input')  
                                    
                    while True:
                            try:
                                h = int(input('Height of the board(2-26):\n'))
                                if h < 27 and h > 1:
                                    break
                                else:
                                    print('Not within bounds')
                            except:
                                print('invalid input')

                    board = [[1] * w for i in range(h)] 
                        #board generated with user's height and width

                    extra_h = extra_row_count(w, 1, agents)
                        
                        
                    auxiliary_1 = [[2] * w]
                        #represents separation row
                    auxiliary_1[0][round(w/2)] = 3
                        #tick button is placed in the middle of the separation row
                    auxiliary_2 = [[1] * w for i in range(extra_h)]
                        #space for the board design tools is added
                    auxiliary = auxiliary_1+auxiliary_2
                        #the two are combined
                        
                    counter = 0
                    for i in range(len(agents)):
                        if i % w == 0:
                            counter += 1
                        auxiliary[counter][i%w] = agents[i]
                        #populated with pieces

                    for i in auxiliary:
                        board.append(i)
                        #adds auxiliaries to board
                        
                    TempBoard = CustomGameBoard(agents, fairies, board, w, h, win_condition)
                        
                    ChessBoard = TempBoard
                
                        

                
                        
                else:
                    print('Invalid answer')

#saving
            if ChessBoard.getboard():
            #if a board has been created
                    presets = []

                    for entry in os.listdir('.\Presets'):
                        presets.append(entry.lower())
                    #creates list of all existing rule sets

                    while True:
                        name = input('Choose a name for your ruleset:\n')
                        if name.lower() in presets:
                            print('Name already taken\n')
                        else:
                            break
                    #verifies that name is unique

                    if name:
                         with open('.\Presets\{}'.format(name), 'wb') as file:
                            pickle.dump(ChessBoard, file)
                    #saves the board object to a file            

#delete
        elif choice == 4:
            presets = []

            for entry in os.listdir('.\Presets'):
                presets.append(entry)

            if presets:
            #verifies that rulesets exist
                print('Select a ruleset from the following to delete...\n')

                print('0: cancel')
                for i in range(len(presets)):
                    print('{}:'.format(i+1), presets[i])
                
                while True:
                    try:
                        choice = int(input(''))
                        if choice >= 0 and choice <= len(presets):
                            break
                        else:
                            print('No such ruleset exists')
                    except:
                        print('Invalid input') 

                if choice == 0:
                    pass
                else:
                    name = presets[choice-1]

                    os.remove('.\Presets\{}'.format(name))
                    #deletes selected ruleset
                    print('Ruleset deleted\n')
            else:
                print('no rulesets currently exist\n') 
                        
#play custom             
        elif choice == 5:

                presets = []

                for entry in os.listdir('.\Presets'):
                    presets.append(entry)
                #presets are loaded from a file

                if presets:
                #verifies that they exist
                    print('Select a ruleset from the following...\n')

                    print('0: cancel')
                    for i in range(len(presets)):
                        print('{}:'.format(i+1), presets[i])

                    while True:
                        try:
                            choice = int(input(''))
                            if choice >= 0 and choice <= len(presets):
                                break
                            else:
                                print('No such ruleset exists')
                        except:
                            print('Invalid input')

                    if choice == 0:
                        pass
                    else:

                        with open('.\Presets\{}'.format(presets[choice-1]), 'rb') as file:
                            ChessBoard = pickle.load(file)

                        #loads selected ruleset

                        custom_pieces = ChessBoard.getfairies()

                        print(custom_pieces)


                        pieces = {
                                  'P':['white_pawn',white_pawn],
                                  'R':['white_rook',white_rook],
                                  'N':['white_knight',white_knight],
                                  'B':['white_bishop',white_bishop],
                                  'K':['white_king',white_king],
                                  'Q':['white_queen',white_queen],
                                  'p':['black_pawn',black_pawn],
                                  'r':['black_rook',black_rook],
                                  'b':['black_bishop',black_bishop],
                                  'n':['black_knight',black_knight],
                                  'k':['black_king',black_king],
                                  'q':['black_queen',black_queen]
                                  }
                        
                        #fills dictionary with custom pieces from loaded ruleset

                        for pair in custom_pieces:
                                for piece in pair:
                                        if piece:
                                                pieces[piece.letter] = [piece.sprite, piece]
                                               
                        #print(pieces) 

                        ChessBoard.create_notation() 
                        ChessBoard.play()

                else:
                    print('No custom rulesets currently exist.\nChoose 2 to play Fischer random+ chess\nChoose 3 to create your own\n')

        
        elif choice == 0:
            print('Invalid answer\n') 
        
            
