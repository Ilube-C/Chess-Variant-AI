#engine

import random

import nltk

names = nltk.corpus.names.words()

from copy import deepcopy

from Mutable_Chess_experimental import *




a = ord('a')
alph = [chr(i) for i in range(a,a+26)]

def boardhash(board):
        hashkey = ''
        for row in board:
                for square in row:
                        hashkey+=str(square)
        return hashkey


def choose_move(moves):
        while True:
                line = moves[random.choice(list(moves.keys()))]
                if not line[2]:
                        pass
                else:
                        piece = line[0]
                        origpos = line[1]
                        move = random.choice(line[2]) 
                        return piece, origpos, move
                


class Engine:
        def __init__(self, board, pieces):
                self.h = len(board)
                self.w = len(board[0])
                self.pieces = pieces
                self.agents = list(pieces.keys())
                self.piece_values = {}
                self.log = []
                self.transposition_table = {}
                for key in self.pieces:
                        self.piece_values[key] = self.eval_piece_vacuum(self.pieces[key][1])
                self.pawn_table = {}
                for x in range(self.h):
                       for y in range(self.w):
                               if board[x][y] == 'p':
                                       self.pawn_table[str(x)+str(y)+'p'] = self.eval_piece([x,y], board, 2)
                               elif board[x][y] == 'P':
                                       self.pawn_table[str(x)+str(y)+'P'] = self.eval_piece([x,y], board, 1)
                                       
                 
                #print(self.piece_values)
                #print(self.generate_moves(board, 1))
                print(self.piece_values)

        def save_game(self):
                name = random.choice(names)
                with open('.\engine_games\{}'.format(name), 'w') as f:
                    for item in self.log:
                        f.write("%s\n" % item)

        def eval_piece_vacuum(self, piece):

                if piece.getStatus() == 'royal':
                        value = 100

                elif piece.getStatus() == 'pawn':
                        value = 8/self.h

                elif piece.getStatus() == 'common':

                        board = [[1] * self.w for i in range(self.h)]

                        total_move_count = 0

                        for a in range(self.h):
                                for b in range(self.w):
                                        i = chr(a+97)
                                        j = str(b + 1)
                                        pos = i+j
                                        #print(pos)
                                        moves = piece.getMoves(pos, board, 1, False, self.w, self.h)
                                        #print(moves)
                                        total_move_count += len(moves)

                        value = round(total_move_count/(0.0390625*((self.h*self.w)**2)), 2)

                return value

        def eval_piece(self, coords, board, turn):

                #print('piece is on {}'.format(coords))  
                value = 0

                piece = self.pieces[board[coords[0]][coords[1]]][1]

                #print('evaluating {}'.format(piece.letter))
                
                value += self.piece_values[piece.letter]

                moves = piece.getMoves(vector_to_algebra([coords[1], coords[0]]), board, turn, True, self.w, self.h)

                if piece.getStatus() == 'pawn':
                        if [str(coords[0])+str(coords[1])+piece.letter] in list(self.pawn_table.keys()):
                                value+=self.pawn_table[coords, piece.letter]
                        else:
                                if piece.letter.isupper():
                                        value+=1.5**(2+coords[0]-self.h)
                                if piece.letter.islower():
                                        value+=1.5**(2-coords[0])
                                self.pawn_table[str(coords[0])+str(coords[1])+piece.letter] = value
                else:
                       
                        for move in moves:
                                #print(move) 
                                value += 0.05*len(moves)
                                coords_temp = algebra_to_vector(move)
                                
                                #print(board[coords_temp[0]][coords_temp[1]]) 
                                if type(board[coords_temp[1]][coords_temp[0]]) is str:
                                        target = board[coords_temp[1]][coords_temp[0]]
                                       
                                        if target.isupper() ^ piece.letter.isupper():
                                                value += 0.05*self.piece_values[target]
                                               
                                        elif not (target.isupper() ^ piece.letter.isupper()):
                                                if self.pieces[target][1].getStatus != 'royal':
                                                        value += 0.025*self.piece_values[target]
                        
                #print('value is {}'.format(value))                
                return value
                                
                

                
                

        def evaluate(self, board):

                try:
                        
                        return self.transposition_table[boardhash(board)]
                except:
                        

                        total_white = 0

                        total_black = 0

                        for a in range(self.h):
                                for b in range(self.w):
                                        if type(board[a][b]) is str:
                                                if (board[a][b]).isupper():
                                                        #print(board[a][b])
                                                        #print(self.eval_piece([a, b], board, 1)) 
                                                        total_white += self.eval_piece([a, b], board, 1)
                                                else:
                                                        #print(board[a][b])
                                                        #print(self.eval_piece([a, b], board, 2)) 
                                                        total_black += self.eval_piece([a, b], board, 2)

                        #print(total_white)

                        #print(total_black)

                        advantage = total_white - total_black

                        self.transposition_table[boardhash(board)] = advantage

                        return advantage
                                                
        def generate_moves(self, board, turn):
                counter = 0  
                piece_moves = {}
                for x in range(self.h):
                       for y in range(self.w):
                               if type(board[x][y]) == str and ((board[x][y]).islower() == turn-1): 
                                       piece_moves[counter] = [board[x][y], [x,y], self.pieces[board[x][y]][1].getMoves(chr(y+97)+str(x+1), board, turn, True, self.w, self.h)]
                                       counter+=1
                for line in piece_moves:
                        if (piece_moves[line][0]) == 'p':
                                for move in piece_moves[line][2]:
                                        if int(move[-1]) == 1:
                                                new_moves = deepcopy(piece_moves[line][2])
                                                new_moves.remove(move)
                                                for p in [p for p in self.agents if (type(p) == str) and p.islower() and p!='p' and p!='k']:
                                                        new_moves.append(move+p)
                                                        piece_moves[line][2] = new_moves
                                                
                        elif (piece_moves[line][0]) == 'P':
                                for move in piece_moves[line][2]:
                                        if int(move[-1]) == self.h:
                                                new_moves = deepcopy(piece_moves[line][2])
                                                new_moves.remove(move)
                                                for p in [p for p in self.agents if (type(p) == str) and p.isupper() and p!='P' and p!='K']:
                                                        new_moves.append(move+p)
                                                        piece_moves[line][2] = new_moves

                #print(piece_moves)

                return piece_moves 
        
        def simulate_move(self, board, move, piece, origpos):
                
                newpos, promotee = algebra_to_vector_2(move)
                                
                board[origpos[0]][origpos[1]] = 1

                                
                if board[newpos[1]][newpos[0]] != 1:
                        previous_positions = []
                        double_previous_positions = []
                                        
                board[newpos[1]][newpos[0]] = piece

                
                if promotee:
                        board, promotee = promotion_check(board, self.h, self.agents, 'engine', 'engine',self.pieces, promotee)
                        previous_positions = []
                        double_previous_positions = []

                return board

        def choose_move(self, board, search_depth, turn):
                
                print(self.minmax_eval(board, search_depth, turn, float('-inf'), float('inf')))
                board, move_info = self.minmax_eval(board, search_depth, turn, float('-inf'), float('inf'))

                print(move_info)
                print('\n')

                self.log.append(move_info[1]+move_info[0])

                return board

        def minmax_eval(self, board, search_depth, turn, alpha, beta, first = True):
                pygame.event.pump()

                #print('call') 

                if search_depth == 0:

                        #print('0')

                        #print(board)

                        return board
                
                if turn == 1:
                        white = True
                else:
                        white = False

                positions = []
                values = []
                move_info = []

                piece_moves = self.generate_moves(board, turn)

                for line in piece_moves:
                        for move in piece_moves[line][2]:
                                tempboard = deepcopy(board)
                                tempboard = self.simulate_move(tempboard, move, piece_moves[line][0], piece_moves[line][1])
                                
                                positions.append(tempboard)
                                move_info.append([move, piece_moves[line][0], piece_moves[line][1]])
                                

                if white:

                        maxEval = float('-inf')
                        
                        if not positions:

                                return board

                                #values.append(self.evaluate(board))

                                #maxEval = max([maxEval, self.evaluate(board)])
                        
                        for position in positions:

                                newboard = self.minmax_eval(position, search_depth-1, next_turn(turn), alpha, beta, False)

                                temp_val = self.evaluate(newboard)

                                
                                values.append(temp_val)

                                maxEval = max([maxEval, temp_val])

                                alpha = max([alpha, temp_val])

                                if beta <= alpha:
                                        break

                        if first:
                                print(move_info)
                                print(values)
                                #print('\n')
                                return positions[values.index(maxEval)], move_info[values.index(maxEval)]

                        return positions[values.index(maxEval)]
                else:
                        minEval = float('inf')

                        if not positions:

                                return board

                                #values.append(self.evaluate(board))

                                #minEval = min([minEval, self.evaluate(board)])

                        for position in positions:

                                newboard = self.minmax_eval(position, search_depth-1, next_turn(turn), alpha, beta, False)

                                temp_val = self.evaluate(newboard)
                                
                                values.append(temp_val)

                                minEval = min([minEval, temp_val])

                                beta = min([beta, temp_val])

                                if beta <= alpha:
                                        break

                        if first:
                                print(move_info)
                                print(values)
                                #print('\n')
                                return positions[values.index(minEval)], move_info[values.index(minEval)]

                        return positions[values.index(minEval)]

                
'''
        def minmax_eval(self, board, search_depth, turn):
                if turn == 1:
                        white = True
                else:
                        white = False

                positions = []
                positions_values = []
                position_dict = {}

                piece_moves = self.generate_moves(board, turn)

                for line in piece_moves:
                        for move in piece_moves[line][2]:
                                tempboard = deepcopy(board)
                                tempboard = self.simulate_move(tempboard, move, piece_moves[line][0], piece_moves[line][1])
                                positions.append(tempboard)
                                key = ''
                                for row in tempboard:
                                        for square in row:
                                                key+=str(square)
                                position_dict[key] = [move, piece_moves[line][0], piece_moves[line][1]]
                                
                if search_depth == 0:
                        positions_values = [self.evaluate(position) for position in positions]
                        if white:
                                return positions[positions_values.index(max(positions_values))], None
                        else:
                                return positions[positions_values.index(min(positions_values))], None
                else:
                        for position in positions:

                                newboard, throwaway = self.minmax_eval(position, search_depth-1, next_turn(turn))

                                positions_values.append(self.evaluate(newboard))

                        if white:
                                board = positions[positions_values.index(max(positions_values))]
                        else:
                                board = positions[positions_values.index(min(positions_values))]
                                
                        key = ''
                        for row in tempboard:
                                for square in row:
                                        key+=str(square)
                        return board, position_dict[key]
'''                        

                        
                


#test = Engine()



                                
                                
