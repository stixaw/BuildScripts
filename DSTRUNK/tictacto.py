import os
import sys
import random

#ugly Global variables
X= "X"
O = "O"
EMPTY = " "
TIE = "TIE"
SQUARES = 9
winner = ''

def instructions():
	print """\t Hello and welcome
	to the tic tac to of DOOM!"""
	print """\tTo make a move you will enter
	a number between 1-8 which 
	coordinates with these squares"""
	print """
		0 | 1 | 2 
		---------
		3 | 4 | 5
		---------
		6 | 7 | 8
		"""
	print "\tPrepare for Battle"

def new_board():
	board = []
	for square in range(SQUARES):
		board.append(EMPTY)
	return board

def display_board(board):
	print "\n\t", board[0], "|", board[1], "|", board[2]
	print "\t", "--------"
	print "\t", board[3], "|", board[4], "|", board[5]
	print "\t", "--------"	
	print "\t", board[6], "|", board[7], "|", board[8], "\n"

def ask_y_n(question):
	response = None
	while response not in ("y", "n"):
		response = raw_input(question).lower()
	return response

def ask_number(question, low, high):
	response = None
	while response not in range (low, high):
		response = int(raw_input(question))
	return response

def pieces():
	go_first = ask_y_n("Do you want to go first? ")
	if go_first == 'y':
		print "then go first, you will need it human"
		human = X
		computer = O
	if go_first == 'n':
		print "Silly human, I will crush you now"
		computer = X
		human = O
	return computer, human
	

def legal_move(board):
	global SQUARES
	moves =[]
	for square in range(SQUARES):
		if board[square] == EMPTY:
			moves.append(square)
	return moves

def findWinner(board):
	ways_to_win = ((0, 1, 2),
			       (3, 4, 5),
			       (6, 7, 8),
			       (0, 3, 6),
			       (1, 4, 7),
			       (2, 5, 8),
			       (0, 4, 8),
			       (2, 4, 6))
	for row in ways_to_win:
		if board[row[0]] == board[row[1]] == board[row[2]] != EMPTY:
			winner == board[row[0]]
			return winner
		if EMPTY not in board:
			return TIE
		return None

def human_move(board, human):
	legal = legal_move(board)
	move = " "
	while move not in legal:
		move = ask_number("what square do you want to move? (0-8): ", 0, SQUARES)
		if move not in legal:
			print "\nThat square is already occupied, foolish human, Choose another!!!!\n"
	print "Fine..."
	return move

def computer_move(board, computer, human):
	board = board[:]
	BEST_MOVES = (4, 0, 2, 6, 8, 1, 3, 5, 7)
	print "I shall take squre number",
	for move in legal_move(board):
		board[move] = computer
		if findWinner(board) == computer:
			print move
			return move
		board[move] = EMPTY
	for move in legal_move(board):
		board[move] = human
		if findWinner(board) == human:
			print move
			return move
		board[move] = EMPTY
	for move in BEST_MOVES:
		if move in legal_move(board):
			print move
			return move

def next_turn(turn):
	if turn == X:
		return O
	else:
		return X

def congrat_winner(winner,computer, human):
	""" Congratulate the winner!"""
	if winner != TIE:
		print winner, "won\n"
	else:
		print "Its a Tie! \n"
	if winner == computer:
		print "la la la I won"
	elif winner == human:
		print "HAXZOR!\n"
	elif winner == TIE:
		print "the sun was in my eyes...."

def Main():
	instructions()
	computer, human = pieces()
	turn = X
	board = new_board()
	display_board(board)

	while not findWinner(board):
		if turn == human:
			move = human_move(board, human)
			board[move] = human
		else:
			move = computer_move(board, computer, human)
			board[move] = computer
		display_board(board)
		turn = next_turn(turn)
	winner = findWinner(board)
	congrat_winner(winner, computer, human)

#start program
Main()
raw_input("\n\nPress enter to exit")
	

	
	


