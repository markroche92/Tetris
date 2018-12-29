import numpy as np
from Utilities import log

# Class for the group of tetris blocks which are fixed at bottom of play area
class ObstacleGroup:

	def __init__(self, width, height):
		self.numberRows, self.numberCols = height, width
		self.value = [[{False : ''} for col in range(width)] for row in range(height)]

	# Check a row of obstacleArray. Output true, if all boxes ar occupied
	def checkRow(self, idxCheck):
		for val in self.value[idxCheck]:
			# Row not fully occupied
			if False in val.keys(): return False
		# Row is fully occupied
		return True

	# Check if the top row of the tetris grid is occupied
	def getMaxRow(self):
		for dct in self.value[0]:
			if dct.keys().__contains__(True): return True
		return False

	# Add piece coordinates to the obstacle array
	@log
	def addToGroup(self, piece, fixRectangleList):
		(offsetRow, offsetCol) = piece.position
		for idxPieceRow, pieceRow in enumerate(piece.value):
			for idxPieceCol, coordValue in enumerate(pieceRow):
				if coordValue == 1:
					rectangle = fixRectangleList[idxPieceRow][idxPieceCol]
					# Update the obstacleArray with the fixed position of the currentPiece
					self.value[offsetRow + idxPieceRow][offsetCol +
					           idxPieceCol] = {True : [piece.colour, rectangle]}

	# Remove specified row from the array
	def removeRow(self, idxRemove):
		# Iteration through list in reverse:
		# https://stackoverflow.com/questions/529424/traverse-a-list-in-reverse-order-in-python
		for idxRow, row in reversed(list(enumerate(self.value))):
			if idxRow == 0:
				# After you remove a row, the first row will always be empty
				self.value[0] = [{False : ''} for col in range(self.numberCols)]

			elif idxRow <= idxRemove:
				# Set each row equal to the previous row that existed
				self.value[idxRow] = self.value[idxRow - 1]



	# Get the indices of the tetris matrix which are occupied by fixed blocks
	def getObstacleIndices(self):
		# Indices are returned as (row, col)
		occupiedIndicesList = []
		for idxRow, row in enumerate(self.value):
			for idxCol, value in enumerate(row):
				if True in value.keys(): occupiedIndicesList.append((idxRow, idxCol))
		return occupiedIndicesList
