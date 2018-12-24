import numpy as np
import random

# Class for any generated current / next playing tetris piece
class TetrisPiece:

    ###################################################################
	######################### Setup Pieces ############################
	###################################################################

	# List of pieces from: https://en.wikipedia.org/wiki/Tetris

	pieceList = {'I' : np.array([[0, 0, 0, 0],
								[1, 1, 1, 1],
								[0, 0, 0, 0],
								[0, 0, 0, 0]]),
				 'J' : np.array([[0, 0, 1, 0],
								[0, 0, 1, 0],
								[0, 1, 1, 0],
								[0, 0, 0, 0]]),
				 'L' : np.array([[0, 1, 1, 0],
								[0, 0, 1, 0],
								[0, 0, 1, 0],
								[0, 0, 0, 0]]),
				 'O' : np.array([[1, 1],
								[1, 1]]),
				 'S' : np.array([[0, 1, 0, 0],
								[0, 1, 1, 0],
								[0, 0, 1, 0],
								[0, 0, 0, 0]]),
				 'T' : np.array([[0, 1, 0, 0],
								[0, 1, 1, 0],
								[0, 1, 0, 0],
								[0, 0, 0, 0]]),
				 'Z' : np.array([[0, 0, 1, 0],
								[0, 1, 1, 0],
								[0, 1, 0, 0],
								[0, 0, 0, 0]])}

	# Block Colors for the game
	pieceColours  = ['red',
				'green2',
				'orchid3',
				'DodgerBlue2',
				'turquoise1',
				'yellow',
				'orange',
				'purple1',
				'gray42',
				'brown']

	def __init__(self, pieceValue = None,
	             piecePosition = None,
				 pieceColour = None,
				 pieceName = None):

		if pieceValue is not None:
			self.value = pieceValue
		elif pieceName and pieceName in self.pieceList.keys():
			# If the pieceName is not None, and it is contained within
			# our list of possible pieces
			self.value = self.pieceList[pieceName]
		else:
			randIdx = random.randint(0, len(list(self.pieceList.keys())) - 1);
			# Else, pick a key at random
			randKey = list(self.pieceList.keys())[randIdx]
			# Get the array values corresponding to the keys
			self.value = self.pieceList[randKey]

		# Choose a colour at random from the colour list
		if pieceColour:
			self.colour = pieceColour
		else:
			self.colour = self.pieceColours[random.randint(0,
			                                       len(self.pieceColours) - 1)]

		for idxRow, row in enumerate(self.value):
			if 1 in row:
				startRow = idxRow
				break
			else: startRow = 0

		# Top Left cornor of the block array may be outside of the tetris frame
		# (Row, Column)
		if piecePosition is not None:
			self.position = piecePosition
		else:
			self.position = np.array((-startRow, 3))

	# Rotate piece values clockwise
	def clockwiseRotation(self):
		# Rotate the array clockwise
		return np.rot90(self.value, axes = (1,0))

	# Rotate piece values counterclockwise
	def counterClockwiseRotation(self):
		# Rotate the array anti-clockwise
		return np.rot90(self.value, axes = (0,1))

	# Get the min column of the block within the tetris grid
	def getPieceMinCol(self, returnGlobal = True):
		minInnerCol = min(np.where(self.value == 1)[1])
		if not returnGlobal: return minInnerCol
		return (minInnerCol + self.position[1])

	# Get the max column of the block within the tetris grid
	def getPieceMaxCol(self, returnGlobal = True):
		maxInnerCol = max(np.where(self.value == 1)[1])
		if not returnGlobal: return maxInnerCol
		return (maxInnerCol + self.position[1])

	# Get the max row of the block within the tetris grid
	def getPieceMaxRow(self, returnGlobal = True):
		maxInnerRow = max(np.where(self.value == 1)[0])
		if not returnGlobal: return maxInnerCol
		return (maxInnerRow + self.position[0])

	# Get the max row of the block within the tetris grid
	def getPieceMinRow(self, returnGlobal = True):
		minInnerRow = min(np.where(self.value == 1)[0])
		if not returnGlobal: return minInnerCol
		return (minInnerRow + self.position[0])

	# Get the global indices of the tetris matrix which are occupied by a tetris piece
	def getPieceGlobalIndices(self):
		# Indices are returned as (row, col)
		occupiedIndicesList = []
		(offsetRows, offsetCols) = self.position
		for idxRow, row in enumerate(self.value):
			for idxCol, value in enumerate(row):
				if value == 1: occupiedIndicesList.append((offsetRows + idxRow,
				                                           offsetCols + idxCol))
		return occupiedIndicesList
