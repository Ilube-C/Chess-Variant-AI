def minmax_eval(self, board, search_depth, turn, alpha, beta, first = True):

        if search_depth == 0:

                return self.evaluate(board)
        
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

                for position in positions:

                        newboard = self.minimax_eval(position, search_depth-1, next_turn(turn), alpha, beta, False)
                        
                        values.append(self.evaluate(newboard))

                        maxEval = max([maxEval, self.evaluate(newboard)])

                        alpha = max([alpha, self.evaluate(newboard)])

                        if beta <= alpha:
                                break

                if first:
                        return maxEval, move_info[values.index(maxEval)]

                return maxEval
        else:
                minEval = float('inf')

                for position in positions:

                        newboard = self.minimax_eval(position, search_depth-1, next_turn(turn), alpha, beta, False)
                        
                        values.append(self.evaluate(newboard))

                        minEval = min([minEval, self.evaluate(newboard)])

                        beta = min([beta, self.evaluate(newboard)])

                        if beta <= alpha:
                                break

                if first:
                        return minEval, move_info[values.index(maxEval)]

                return minEval
                        
                        
                        
