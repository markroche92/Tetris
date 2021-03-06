import numpy as np
from enum import Enum
import random

class PieceSet(Enum):
    TETRAMINO = 1
    QUADRAMINO = 2
    SEXTAMINO = 3

# Class for any generated current / next playing tetris piece
class TetrisPiece:

    ###################################################################
	######################### Setup Pieces ############################
	###################################################################

	# List of pieces from: https://en.wikipedia.org/wiki/Tetris
	tetraminos = {'I' : np.array([[0, 0, 0, 0],
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

	# Pentaminos: https://www.google.com/search?q=five+block+tetris+pieces%5D&tbm=isch&source=iu&ictx=1&fir=_qutxsXCltkBdM%253A%252CsVrnaNJQbyTqRM%252C_&usg=AI4_-kRwBF_ktMhFZVUXDQDUwDip4m38VQ&sa=X&ved=2ahUKEwjHzb_4trnfAhWtRxUIHWP5ARUQ9QEwC3oECAEQCA#imgrc=BzsmtcMA9QUWiM:
	pentaminos = {'I2' : np.array([[0, 0, 0, 0],
								[1, 1, 1, 1],
								[0, 1, 0, 0],
								[0, 0, 0, 0]]),
				'I3' : np.array([[0, 1, 0, 0],
								[1, 1, 1, 1],
								[0, 0, 0, 0],
								[0, 0, 0, 0]]),
				'J2' : np.array([[0, 0, 0, 0],
								[1, 1, 1, 1],
								[0, 0, 0, 1],
								[0, 0, 0, 0]]),
				'L2' : np.array([[0, 0, 0, 0],
								[0, 0, 0, 1],
								[1, 1, 1, 1],
								[0, 0, 0, 0]]),
				'Q' : np.array([[0, 1, 1, 0],
								[0, 1, 1, 0],
								[0, 0, 1, 0],
								[0, 0, 0, 0]]),
				'P' : np.array([[0, 1, 1, 0],
								[0, 1, 1, 0],
								[0, 1, 0, 0],
								[0, 0, 0, 0]]),
				'C' : np.array([[0, 1, 1, 0],
								[0, 1, 0, 0],
								[0, 1, 1, 0],
								[0, 0, 0, 0]]),
				'S2' : np.array([[0, 0, 0, 0],
								[0, 1, 1, 1],
								[1, 1, 0, 0],
								[0, 0, 0, 0]]),
				'Z2' : np.array([[0, 0, 0, 0],
								[1, 1, 0, 0],
								[0, 1, 1, 1],
								[0, 0, 0, 0]])}

	sextaminos = {'I4' : np.array([[0, 1, 1, 0],
								[0, 1, 1, 0],
								[0, 1, 1, 0],
								[0, 0, 0, 0]]),
				'G' : np.array([[0, 0, 0, 0],
								[1, 1, 1, 1],
								[1, 1, 0, 0],
								[0, 0, 0, 0]]),
				'D' : np.array([[0, 0, 0, 0],
								[1, 1, 1, 1],
								[0, 0, 1, 1],
								[0, 0, 0, 0]]),
				'U' : np.array([[0, 0, 0, 0],
								[1, 0, 0, 1],
								[1, 1, 1, 1],
								[0, 0, 0, 0]]),
				'PI' : np.array([[0, 0, 0, 0],
								[1, 1, 1, 1],
								[0, 1, 1, 0],
								[0, 0, 0, 0]]),
				'J3' : np.array([[0, 0, 0, 0],
								[1, 1, 1, 1],
								[0, 0, 0, 1],
								[0, 0, 0, 1]]),
				'L3' : np.array([[0, 0, 0, 1],
								[0, 0, 0, 1],
								[1, 1, 1, 1],
								[0, 0, 0, 0]]),
				'W' : np.array([[0, 0, 0, 0],
								[0, 0, 0, 1],
								[0, 1, 1, 1],
								[1, 1, 0, 0]])}

	# Block Colors for the game
	turquoiseColours  = ['turquoise1', 'turquoise2', 'turquoise3', 'turquoise4']
	goldenColours = ['goldenrod1', 'goldenrod2', 'goldenrod3', 'goldenrod4']
	orchidColours = ['DarkOrchid1', 'DarkOrchid2', 'DarkOrchid3', 'DarkOrchid4']

	colours = [turquoiseColours, goldenColours, orchidColours]
	colourSets = [set(sublist) for sublist in colours]
	allColours = list(set().union(*colourSets))

	level2Set = [set(sublist) for sublist in colours[0:2]]
	level2 = list(set().union(*level2Set))

	def __init__(self, pieceSet = None, pieceValue = None,
	             piecePosition = None,
				 pieceColour = None,
				 pieceName = None):

		if pieceSet == PieceSet.TETRAMINO:
			self.pieceList = self.tetraminos
			self.pieceColours = self.turquoiseColours
		elif pieceSet == PieceSet.QUADRAMINO:
			self.pieceList = {**self.tetraminos, **self.pentaminos}
			self.pieceColours = self.level2
		elif pieceSet == PieceSet.SEXTAMINO:
			self.pieceList = {**self.tetraminos, **self.pentaminos, **self.sextaminos}
			self.pieceColours = self.allColours

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
