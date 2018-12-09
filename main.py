from tkinter import *
from math import floor
from enum import Enum
import numpy as np
import time
import random
import math
import curses
import sys
import copy

class DisplayType(Enum):
	SCORE = 0
	LEVEL = 1

class TetrisPiece:

    ###################################################################
	######################### Setup Pieces ############################
	###################################################################

	# List of pieces from: https://en.wikipedia.org/wiki/Tetris

	pieceList = {'I' : np.array([[0, 0, 0, 0],
								[1, 1, 1, 1],
								[0, 0, 0, 0],
								[0, 0, 0, 0]]),
				 'J' : np.array([[0, 0, 0],
								[1, 1, 1],
								[0, 0, 1]]),
				 'L' : np.array([[0, 0, 0],
								[1, 1, 1],
								[1, 0, 0]]),
				 'O' : np.array([[1, 1],
								[1, 1]]),
				 'S' : np.array([[0, 0, 0],
								[0, 1, 1],
								[1, 1, 0]]),
				 'T' : np.array([[0, 1, 0],
								[1, 1, 1],
								[0, 0, 0]]),
				 'Z' : np.array([[1, 1, 0],
								[0, 1, 1],
								[0, 0, 0]])}

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

	def __init__(self, pieceValue = None, piecePosition = None, pieceColour = None, pieceName = None):

		if pieceValue is not None:
			self.value = pieceValue
		elif pieceName and pieceName in self.pieceList.keys():
			# If the pieceName is not None, and it is contained within our list of possible pieces
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
			self.colour = self.pieceColours[random.randint(0, len(self.pieceColours) - 1)]

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

	def clockwiseRotation(self):
		# Rotate the array clockwise
		return np.rot90(self.value, axes = (1,0))

	def counterClockwiseRotation(self):
		# Rotate the array anti-clockwise
		return np.rot90(self.value, axes = (0,1))


class TetrisGame:
	# Window width and height
	windowWidth, windowHeight = 480, 480

	# Design dimensions
	tetrisHeight, tetrisWidth = 400, 200

	# Button / Label height
	labelFrameHeightLen = 40

	## Number of rows and columns in the grid
	numberRows, numberCols = 24, 24
	maxRow, maxCol, minRow, minCol = numberRows - 1, numberCols - 1, 0, 0

	# Calculate gridWidth
	gridWidth = int(windowHeight / numberRows)

	# Calculate the length allowed for the next block frame
	nextBlockFrameHeightLen = (windowHeight - 3 * labelFrameHeightLen -
						   	   gridWidth * 7)

	# Width for the the right frame
	rightFrameWidth = (windowWidth - tetrisWidth - 6 * gridWidth)

	# Placement of frames on Y axis
	# Note: These measurements are taken from the base of rightFrame
	scoreFramePlaceY = gridWidth
	levelFramePlaceY = 2 * gridWidth + labelFrameHeightLen
	nextBlockFramePlaceY = gridWidth * 3 + 2 * labelFrameHeightLen
	startFramePlaceY = windowHeight - gridWidth * 3 - labelFrameHeightLen

	# Calculate Tetris Grid Parameters
	numberRowsTetris, numberColsTetris = (int(tetrisHeight / gridWidth),
	                                      int(tetrisWidth / gridWidth))

	# Number of digits in the score / level number
	scoreNumberDigits, levelNumberDigits = 10, 4

	# Score Pre-String
	scoreBaseStr = "Score:"
	# Level Pre-String
	levelBaseStr = "Level:"

	# Block Colors for the game
	blockColors  = ['red',
				'green2',
				'orchid3',
				'DodgerBlue2',
				'turquoise1',
				'yellow',
				'orange',
				'purple1',
				'gray42',
				'brown']

	def __init__(self, root, cursesWindow):

		# Set up the window and borders for display
		self.root = root
		self.cursesWindow = cursesWindow
		self.cursesWindow.nodelay(1)

		# Initialise the Score Sting
		self.scoreString = StringVar()
		self.scoreString.set('{} {}'.format(self.scoreBaseStr, "0000000000"))

		# Initialise the Score Sting
		self.levelString = StringVar()
		self.levelString.set('{} {}'.format(self.levelBaseStr, "0000"))

		# Window placement, dimensions etc.
		self.setRootProperties()

		self.mainFrame = Frame(self.root, height = self.windowHeight,
		                       width = self.windowWidth, bg = 'white')

	    # mainFrame occupies the full window
		self.mainFrame.grid()

	    ###################################################################
		######################### Set Up Window ###########################
		###################################################################

		# Window Border Creation
		windowBorderNorth = Frame(self.mainFrame, height = self.gridWidth,
		                          width = self.windowWidth - self.gridWidth, bg = 'SeaGreen1')
		windowBorderWest = Frame(self.mainFrame, height = self.windowHeight - self.gridWidth,
		                         width = self.gridWidth, bg = 'SeaGreen1')
		windowBorderSouth = Frame(self.mainFrame, height = self.gridWidth,
		                          width = self.windowWidth  - self.gridWidth, bg = 'SeaGreen1')
		windowBorderEast = Frame(self.mainFrame, height = self.windowHeight  - self.gridWidth,
		                         width = self.gridWidth, bg = 'SeaGreen1')

	 	# Window Border Placement
		windowBorderNorth.grid(row = self.minRow, column = self.minCol,
		                       columnspan = self.numberCols - 1, sticky = 'N')
		windowBorderWest.grid(row = self.minRow + 1, column = self.minCol,
		                      rowspan = self.numberRows - 1, sticky = 'W')
		# Tetris Parent Frame
		xLimit = self.tetrisWidth + 2 * self.gridWidth
		yLimit = self.tetrisHeight + 2 * self.gridWidth
		tetrisParent = Frame(self.mainFrame, height = yLimit, width = xLimit, bg = 'orange')
		tetrisParent.grid(row = self.minRow + 1, column = self.minCol + 1,
		                  rowspan = self.numberRows - 2, sticky = 'W')
		self.canvasTetrisBorder = Canvas(tetrisParent, height = yLimit, width = xLimit, bg = 'gray71')
		# https://stackoverflow.com/questions/4310489/how-do-i-remove-the-light-grey-border-around-my-canvas-widget
		self.canvasTetrisBorder.config(highlightthickness = 0)
		self.drawGrid(self.canvasTetrisBorder, xLimit = xLimit, yLimit = yLimit)
		self.canvasTetrisBorder.place(x = 0, y = 0)


		# Tetris Frame
		tetrisFrame = Frame(tetrisParent, height = self.tetrisHeight,
		                     width = self.tetrisWidth, bg = 'black')
		tetrisFrame.place(x = self.gridWidth, y = self.gridWidth)
		self.canvasTetris = Canvas(tetrisFrame, height = yLimit, width = xLimit, bg = 'black')
		# https://stackoverflow.com/questions/4310489/how-do-i-remove-the-light-grey-border-around-my-canvas-widget
		self.canvasTetris.config(highlightthickness = 0)
		self.canvasTetris.place(x = 0, y = 0)


		# Right Frame
		rightFrame = Frame(self.mainFrame, height = self.tetrisHeight + 2 * self.gridWidth,
		                     width = self.windowWidth - self.tetrisWidth - 4 * self.gridWidth, bg = 'black')
		rightFrame.grid(row = self.minRow + 1, column = 1 + self.numberColsTetris + 2, sticky = 'W')

		# Score
		# .place() command parameters: http://effbot.org/tkinterbook/place.htm
		scoreFrame = Frame(rightFrame, bg = 'black', height = self.labelFrameHeightLen,
		                   width = self.rightFrameWidth)
		scoreLabel = Label(scoreFrame, textvariable = self.scoreString)
		scoreLabel.config(font=("Helvetica", 10))
		scoreLabel.place(relx = 0.5, rely = 0.5, relwidth=1, relheight=1, anchor = CENTER)
		scoreFrame.place(x = self.gridWidth , y = self.scoreFramePlaceY)

		# Level
		# .place() command parameters: http://effbot.org/tkinterbook/place.htm
		levelFrame = Frame(rightFrame, bg = 'black', height = self.labelFrameHeightLen,
		                   width = self.rightFrameWidth)
		levelLabel = Label(levelFrame, textvariable = self.levelString)
		levelLabel.config(font=("Helvetica", 10))
		levelLabel.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor=CENTER)
		levelFrame.place(x = self.gridWidth , y = self.levelFramePlaceY)

		# Next Block
		# Field for displaying the next piece
		nextBlockFrame = Frame(rightFrame, bg = 'white', height = self.nextBlockFrameHeightLen,
		                       width = self.rightFrameWidth)
		nextBlockFrame.place(x = self.gridWidth, y = self.nextBlockFramePlaceY)

		# Start / Pause Button
		# .place() command parameters: http://effbot.org/tkinterbook/place.htm
		startFrame = Frame(rightFrame, bg = 'black', height = self.labelFrameHeightLen,
						   width = self.windowWidth - self.tetrisWidth - 6 * self.gridWidth)
		self.startButton = Button(startFrame, text = "Start /Pause Game", command = self.clickStartButton)
		self.startButton.config(font=("Helvetica", 10))
		self.startButton.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor=CENTER)
		startFrame.place(x = self.gridWidth, y = self.startFramePlaceY)

		# Window Borders South and East
		windowBorderSouth.grid(column = self.minCol + 1, row = self.maxRow,
		                       columnspan = self.numberCols - 1, sticky = 'S')
		windowBorderEast.grid(row = self.minRow, column = self.maxCol,
		                      rowspan = self.numberRows - 1, sticky = 'E')

	    ###################################################################
		###################################################################

	    ###################################################################
		######################## Game Parameters ##########################
		###################################################################

		self.score = 0
		self.level = 1
		self.alive = True
		self.loading = True
		self.currentPiece = None
		self.renderList = []
		# Each sublist represents a row of the tetris grid
		# Each element in the sublist represents a cell in the row
		# First sublist represents the top of the tetris grid
		# Dictionary is Boolean : String. Boolean: Is the cell occupied?  String: What is the color of the occupying block
		# Work with this variable as obstacleArray[row (0 based)][column (0 based)]
		self.obstacleArray = [[{False : ''} for col in range(self.numberColsTetris)] for row in range(self.numberRowsTetris)]

	    ###################################################################
		###################################################################

	# Generate a random block of random color
	def spawnBlock(self):

		# Choose a block from dictionary
		self.currentPiece = TetrisPiece();

	# Return numpy array of x and y co-ordinates corresponding to a grid from (0,0)
	# to specified limit
	def drawGrid(self, canvas, xLimit, yLimit):
		# Get vectors of co-ordinates
		xVector = np.linspace(0, xLimit, xLimit / self.gridWidth + 1)
		yVector = np.linspace(0, yLimit, yLimit / self.gridWidth + 1)
		# Draw grid
		[canvas.create_line(xCoord, 0, xCoord , self.tetrisHeight + 2 * self.gridWidth) for xCoord in xVector]
		[canvas.create_line(0, yCoord, self.tetrisWidth + 2 * self.gridWidth, yCoord) for yCoord in yVector]

	# Update the score displayed
	def updateDisplay(self, newValue, displayType):

		if displayType is DisplayType.SCORE:
			valueMaxLength = self.scoreNumberDigits
		elif displayType is DisplayType.LEVEL:
			valueMaxLength = self.levelNumberDigits
		else:
			self.alive = False
			self.root.destroy()
			raise Exception('Unrecognised displayType ''{}'' in function updateDisplay()'.format(displayType))

		# Convert the new score to string
		newValueStr = str(newValue)
		# Add extra zeros to beginning of score number
		if (valueMaxLength > len(newValueStr)):
			newValueStrFull = ''.join([''.join('0' for idx in range(valueMaxLength - len(newValueStr))), newValueStr])
			# Update the displayed score
			if displayType is DisplayType.SCORE:
				self.scoreString.set('{} {}'.format(self.scoreBaseStr , newValueStrFull))
			elif displayType is DisplayType.LEVEL:
				self.levelString.set('{} {}'.format(self.levelBaseStr , newValueStrFull))
		else:
			print("You reached the max score {} - Congratulations!".format(newValueStr))
			# Flag exits the application running loop
			self.alive = False
			self.root.destroy()

	# Window placement, dimensions and properties
	def setRootProperties(self):
		## Set window properties
		# Window stays in front of other windows until closed
		self.root.attributes("-topmost", True)
		self.root.configure(background = 'black')
		self.root.title('Tetris Application')

		# Window is not resizeable in X or Y directions
		# https://stackoverflow.com/questions/21958534/how-can-i-prevent-a-window-from-being-resized-with-tkinter
		self.root.resizable(width=False, height=False)

		## Set window position and dimensions
		# Width and Height of the user's computer screen
		# https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
		screenWidth = self.root.winfo_screenwidth()
		screenHeight = self.root.winfo_screenheight()

		# Initial X and Y position of the window - centre the window in the screen
		windowX = floor(screenWidth / 2) - floor(self.windowWidth / 2)
		windowY = floor(screenHeight / 2) - floor(self.windowHeight / 2)

		# Set window position and dimensions
		self.root.geometry('{}x{}+{}+{}'.format(self.windowWidth,
									            self.windowHeight,
									            windowX,
									            windowY))

    # Color the grid cell in the specified location
	def colorCell(self, xCoord, yCoord, color):
		self.canvasTetris.create_rectangle(xCoord * self.gridWidth, yCoord * self.gridWidth,
		                                   (xCoord + 1) * self.gridWidth,
										   (yCoord + 1) * self.gridWidth, fill = color)

	# Update gameArea cells
	def updateCells(self, cellDict):
		# Color each cell based on the color value
		# Iin dictionary, coordiates are key tuple, color is value
		for cell in cellDict:
			# Extract the X and Y Co-ordinates of the cell of interest
			(xCoord, yCoord) = cell
			# Extract the required color
			color = cellDict[cell]
			# Update the Canvas in
			self.colorCell(xCoord, yCoord, color)

	def clearLoadingScreen(self):

		self.canvasTetrisBorder.config(bg = 'gray71')

		for idxRow in range(self.numberRowsTetris):
			for idxCol in range(self.numberColsTetris):
				self.updateCells({(idxCol, idxRow): 'black'})

	# Display the loading screen to the player
	def runLoadingScreen(self):

		# When tetris border changes color, the game is paused
		self.canvasTetrisBorder.config(bg = 'gold')
		idxRowBase = 0
		# Randomly initialise the tilt of the blocks shown on the loading screen
		factorTilt = random.choice(range(-self.numberRowsTetris + 1, self.numberRowsTetris - 1))
		# Randomly initialise the speed of the loading screen
		speedInit = random.randint(5, 500) / 1000
		while (self.loading):
			# Increment the loop while alive
			idxRowBase = idxRowBase + 1
			# Don't allow the row index to exceed 19
			idxRowBase = idxRowBase % self.numberRowsTetris
			# speed = speedInit * math.sin(math.pi * (idxBase / 19))
			time.sleep(speedInit)
			for idxColor, color in enumerate(self.blockColors):
				# Don't allow the processed row index exceed 19
				idxRowTilt = (idxRowBase + factorTilt * idxColor) % 20
				# Don't allow the processed previous row index exceed 19
				idxRowPrev = idxRowTilt - 1 if idxRowTilt != 0 else 19
				# Reset the previous cell in the column to color black
				self.updateCells({(idxColor, idxRowPrev): 'black'})
				# Reset the next cell in the column to required color
				self.updateCells({(idxColor, idxRowTilt): color})

			if idxRowBase % 10 < 5:
				self.startButton.config(bg='SeaGreen1')
			elif idxRowBase % 10 >= 5:
				self.startButton.config(bg='white')
			# Update the display as long as the game hasn't been closed
			if self.loading: self.root.update()

		self.clearLoadingScreen()

	# Dictate what happens when the start button is clicked
	def clickStartButton(self):
		self.loading = not self.loading

	# Update the position of the current piece under player control
	def gravity(self):

		copyPiece = copy.deepcopy(self.currentPiece)
		copyPiece.position[0] = min(self.numberRowsTetris,
                                    copyPiece.position[0] + 1)
		copyPieceIndices = set(self.getPieceIndices(copyPiece))
		obstacleIndices = set(self.getObstacleIndices())

		if (self.getPieceMaxRow(copyPiece) > self.numberRowsTetris - 1 or
		    set.intersection(obstacleIndices, copyPieceIndices)):

			self.renderPieceOnScreen(fix = True)
			self.addToObstacleArray()
			self.currentPiece = None
		else:
			# Update the position of the block base on the action of gravity
			# Update ROW
			self.currentPiece.position[0] = min(self.numberRowsTetris,
			                                    self.currentPiece.position[0] + 1)
			self.renderPieceOnScreen(fix = False)

	    ###################################################################
		###################################################################

	# Add piece coordinates to the obstacle array
	def addToObstacleArray(self):
		(offsetRow, offsetCol) = self.currentPiece.position
		for idxPieceRow, pieceRow in enumerate(self.currentPiece.value):
			for idxPieceCol, coordValue in enumerate(pieceRow):
				if coordValue == 1:
					# Update the obstacleArray with the fixed position of the currentPiece
					self.obstacleArray[offsetRow + idxPieceRow][offsetCol +
					                   idxPieceCol] = {True : self.currentPiece.colour}

	# Remove specified row from the array
	def removeRowObstacleArray(self, idxRemove):
		# Iteration through list in reverse:
		# https://stackoverflow.com/questions/529424/traverse-a-list-in-reverse-order-in-python
		for idxRow, row in reversed(list(enumerate(self.obstacleArray))):
			if idxRow == 0:
				# After you remove a row, the first row will always be empty
				self.obstacleArray[0] = [{False : ''} for col in range(self.numberColsTetris)]
			elif idxRow <= idxRemove:
				# Set each row equal to the previous row that existed
				self.obstacleArray[idxRow] = self.obstacleArray[idxRow - 1]

	# Check a row of obstacleArray. Output true, if all boxes ar occupied
	def checkRowObstacleArray(self, idxCheck):
		for value in self.obstacleArray[idxCheck]:
			# Row not fully occupied
			if False in value.keys(): return False
		# Row is fully occupied
		return True

	# Run loop where user input is processed
	def userInput(self):
		# Measure the initial time
		#timeInit = time.clock()
		#curTime = timeInit
		cnt = 0

		# Allow user inputs for a certain period of timeMax
		while(cnt < 10000):
			#curTime = time.clock()
			cnt = cnt + 1
			key = self.cursesWindow.getch()
			#self.cursesWindow.addstr(str(time.clock() - timeInit) + " ")
			# If there is a use input
			if key != -1:
				obstacleIndices = set(self.getObstacleIndices())
			if key == ord('d'):

				rotatedPiece = TetrisPiece(pieceValue = self.currentPiece.clockwiseRotation(),
				 						   piecePosition = self.currentPiece.position,
										   pieceColour = self.currentPiece.colour)

				rotatedIndices = set(self.getPieceIndices(rotatedPiece))

				if (self.getPieceMinCol(rotatedPiece) > -1 and
					self.getPieceMaxCol(rotatedPiece) < self.numberColsTetris and
					self.getPieceMaxRow(rotatedPiece) < self.numberRowsTetris and
					not set.intersection(rotatedIndices, obstacleIndices)):
					self.cursesWindow.addstr('GOT KEY D')
					self.currentPiece.value = self.currentPiece.clockwiseRotation()
					#break
				#self.root.update()
			elif key == ord('a'):
				rotatedPiece = TetrisPiece(pieceValue = self.currentPiece.counterClockwiseRotation(),
				 						   piecePosition = self.currentPiece.position,
										   pieceColour = self.currentPiece.colour)

				rotatedIndices = set(self.getPieceIndices(rotatedPiece))

				if (self.getPieceMinCol(rotatedPiece) > -1 and
				    self.getPieceMaxCol(rotatedPiece) < self.numberColsTetris and
					self.getPieceMaxRow(rotatedPiece) < self.numberRowsTetris and
					not set.intersection(rotatedIndices, obstacleIndices)):
					#self.cursesWindow.addstr('GOT KEY A')
					self.currentPiece.value = self.currentPiece.counterClockwiseRotation()
					#break
				#self.root.update()
			elif (key == curses.KEY_LEFT and
			     self.getPieceMinCol(self.currentPiece) > 0):
				#self.cursesWindow.addstr('MOVE LEFT')

				copyPiece = copy.deepcopy(self.currentPiece)
				copyPiece.position[1] = copyPiece.position[1] - 1
				copyPieceIndices = set(self.getPieceIndices(copyPiece))

				if not set.intersection(copyPieceIndices, obstacleIndices):
					minInnerCol = min(np.where(self.currentPiece.value == 1)[1])
					self.currentPiece.position[1] = max(-minInnerCol,
					                                    self.currentPiece.position[1] - 1)
					#break
			elif (key == curses.KEY_RIGHT and
			     self.getPieceMaxCol(self.currentPiece) < self.numberColsTetris - 1):

				copyPiece = copy.deepcopy(self.currentPiece)
				copyPiece.position[1] = copyPiece.position[1] + 1
				copyPieceIndices = set(self.getPieceIndices(copyPiece))

				if not set.intersection(copyPieceIndices, obstacleIndices):
					#self.cursesWindow.addstr('MOVE RIGHT')
					self.currentPiece.position[1] = min(self.numberColsTetris,
					                                    self.currentPiece.position[1] + 1)
					#break
		#self.cursesWindow.addstr('BROKEN!')

	# Function to render the piece on the screen
	def renderPieceOnScreen(self, fix):
		# Reset the previous rendering to black
		if self.renderList:
			for point in self.renderList:
				# Point is (Row, Col), i.e. (Y, X)
				self.colorCell(point[1], point[0], 'black')

		# Render the block's new position
		self.renderList = []
		(offsetRows, offsetCols) = self.currentPiece.position
		for idxRow, row in enumerate(self.currentPiece.value):
			for idxCol, value in enumerate(row):
				if value == 1:
					# Remember that we are rendering these indices of the grid
					if not fix:
						self.renderList.append((offsetRows + idxRow, offsetCols + idxCol))
					self.colorCell(offsetCols + idxCol, offsetRows + idxRow, self.currentPiece.colour)

	# get the min column of the block within the tetris grid
	def getPieceMinCol(self, piece):
		minInnerCol = min(np.where(piece.value == 1)[1])
		return (minInnerCol + piece.position[1])

	# get the max column of the block within the tetris grid
	def getPieceMaxCol(self, piece):
		maxInnerCol = max(np.where(piece.value == 1)[1])
		return (maxInnerCol + piece.position[1])

	# get the max row of the block within the tetris grid
	def getPieceMaxRow(self, piece):
		maxInnerRow = max(np.where(piece.value == 1)[0])
		return (maxInnerRow + piece.position[0])

	# Get the indices of the tetris matrix which are occupied by fixed blocks
	def getObstacleIndices(self):
		# Indices are returned as (row, col)
		occupiedIndicesList = []
		for idxRow, row in enumerate(self.obstacleArray):
			for idxCol, value in enumerate(row):
				if True in value.keys(): occupiedIndicesList.append((idxRow, idxCol))
		return occupiedIndicesList

	# Get the global indices of the tetris matrix which are occupied by a tetris piece
	def getPieceIndices(self, piece):
		# Indices are returned as (row, col)
		occupiedIndicesList = []
		(offsetRows, offsetCols) = piece.position
		for idxRow, row in enumerate(piece.value):
			for idxCol, value in enumerate(row):
				if value == 1: occupiedIndicesList.append((offsetRows + idxRow,
				                                           offsetCols + idxCol))
		return occupiedIndicesList

	# Remove any rows which are now complete
	def removeRows(self):
		doRemove = False
		for idxRow in range(self.numberRowsTetris):
			if self.checkRowObstacleArray(idxRow):
				doRemove = True
				self.removeRowObstacleArray(idxRow)
				self.score = self.score + 100
				self.updateDisplay(self.score, DisplayType.SCORE)
		if doRemove: self.renderObstaclesOnScreen()

	# Render the fixed objects on the screen
	def renderObstaclesOnScreen(self):
		# Once rows have been removed, render the obstacles on the screen

		for idxRow, row in enumerate(self.obstacleArray):
			for idxCol, dct in enumerate(row):
				if True in dct.keys():
					self.colorCell(idxCol, idxRow, dct[True])
				else:
					self.colorCell(idxCol, idxRow, 'black')

	# Render empty screen
	def renderEmptyScreen(self):
		for idxRow in range(self.numberRowsTetris):
			for idxCol in range(self.numberColsTetris):
				self.colorCell(idxCol, idxRow, 'black')


def main(window):
	root = Tk()
	Game = TetrisGame(root = root, cursesWindow = window)
	wasLoading = False
	while (Game.alive):
		if Game.loading:
			#window.addstr('LOADING ')
			# Show loading screen until not loading
			# runLoadingScreen() contains a while() running at random speed
			# Note: Game.runLoadingScreen() contains root.update()
			if not wasLoading: Game.renderEmptyScreen()
			Game.runLoadingScreen()
			wasLoading = True
		else:
			if wasLoading: Game.renderObstaclesOnScreen()
			wasLoading = False
			#window.addstr('loop ')
			if Game.currentPiece:
				#window.addstr('START USER IN ')
				Game.userInput()
				#window.addstr('START GRAVITY ')
				Game.gravity()
				Game.removeRows()
			else:
				#window.addstr('SPAWN BLOCK ')
				Game.spawnBlock()
		#window.addstr('ROOT UPDATE ')
		root.update()

curses.wrapper(main)

## Actions:
# If loading, show loading screen.
# If not loading:
# - *** Control should be X (2?) times as fast as gravity **
# - * If not controlling a block: Spawn a random block
# - * User control time: rotation, movement of this block (do not fix block until gravity timer complete)
# - ** Gravity time: If block can move down, go to very start of Actions
# Postprocessing after movement
#  If block cannot move down fix the block into the structure.
# - Assess the matrix of fixed blocks. Remove any complete rows.
# - Move the contents above the lowest deleted row, down to the last empty cell before an unempty cell
# - Set Game.currentBlock = None
