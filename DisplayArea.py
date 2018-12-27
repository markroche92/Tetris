from BorderedFrame import BorderedFrame
from tkinter import *
from math import floor
from enum import Enum
import numpy as np
import random
import time
from TetrisPiece import TetrisPiece
import curses



# Window placement, dimensions and properties
def setRootProperties(root, windowHeight, windowWidth, background = 'black', title = 'Tetris Application'):
	## Set window properties
	# Window stays in front of other windows until closed
	root.attributes("-topmost", True)
	root.configure(background = background)
	root.title(title)

	# Window is not resizeable in X or Y directions
	# https://stackoverflow.com/questions/21958534/how-can-i-prevent-a-window-from-being-resized-with-tkinter
	root.resizable(width=False, height=False)

	## Set window position and dimensions
	# Width and Height of the user's computer screen
	# https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
	screenWidth = root.winfo_screenwidth()
	screenHeight = root.winfo_screenheight()

	# Initial X and Y position of the window - centre the window in the screen
	windowX = floor(screenWidth / 2) - floor(windowWidth / 2)
	windowY = floor(screenHeight / 2) - floor(windowHeight / 2)

	# Set window position and dimensions
	root.geometry('{}x{}+{}+{}'.format(windowWidth,
							            windowHeight,
							            windowX,
							            windowY))
	return root

class DisplayType(Enum):
	SCORE = 0
	LEVEL = 1

# Class for the display area
class DisplayArea:

	# Window width and height
	windowWidth, windowHeight = 480, 480

	# Design dimensions
	tetrisHeight, tetrisWidth = 400, 200

	# Button / Label height
	labelFrameHeightLen = 20

	## Number of rows and columns in the grid
	numberRows, numberCols = 24, 24
	maxRow, maxCol, minRow, minCol = numberRows - 1, numberCols - 1, 0, 0

	# Calculate gridWidth
	gridWidth = int(windowHeight / numberRows)

	# Calculate Tetris Grid Parameters
	numberRowsTetris, numberColsTetris = (int(tetrisHeight / gridWidth),
	                                      int(tetrisWidth / gridWidth))

	# Calculate the length allowed for the next block frame
	nextBlockFrameHeightLen = (windowHeight - 4 * labelFrameHeightLen -
						   	   gridWidth * 9)

	# Width for the the right frame
	rightFrameWidth = (windowWidth - tetrisWidth - 6 * gridWidth)

	# Placement of frames on Y axis
	# Note: These measurements are taken from the base of rightFrame
	scoreFramePlaceY = gridWidth
	levelFramePlaceY = 2 * gridWidth + labelFrameHeightLen
	nextBlockFramePlaceY = gridWidth * 3 + 2 * labelFrameHeightLen
	startFramePlaceY = windowHeight - gridWidth * 3 - labelFrameHeightLen

	# Number of digits in the score / level number
	scoreNumberDigits, levelNumberDigits = 5, 3

	# Score Pre-String
	scoreBaseStr = "Score:"
	# Level Pre-String
	levelBaseStr = "Level:"
	# Next Piece StringVar
	nextPieceStr = 'Next Piece:'

	def __init__(self, root, cursesWindow, gameObject):

		# Set up the window and borders for display
		self.game = gameObject
		self.root = root
		self.cursesWindow = cursesWindow
		self.cursesWindow.nodelay(1)

		# Initialise the Score Sting
		self.scoreString = StringVar()
		self.scoreString.set('{} {}'.format(self.scoreBaseStr, "00000"))

		# Initialise the Score Sting
		self.levelString = StringVar()
		self.levelString.set('{} {}'.format(self.levelBaseStr, "000"))

		# Set the Next Piece String (not to change over cource of program)
		nextPieceString = StringVar()
		nextPieceString.set(self.nextPieceStr)

		# Window placement, dimensions etc.
		self.root = setRootProperties(self.root, self.windowHeight, self.windowWidth)

		self.mainFrame = Frame(self.root, height = self.windowHeight,
		                       width = self.windowWidth, bg = 'white')

		# mainFrame occupies the full window
		self.mainFrame.grid()

		###################################################################
		######################### Set Up Window ###########################
		###################################################################

		# Create Main Window (Bordered)
		windowBorder = BorderedFrame(self.mainFrame, self.gridWidth,
		                             self.windowWidth, self.windowHeight,
									 self.createTetrisPlayArea, 'SeaGreen1')

        ###################################################################
        ###################################################################

    # Function to create content within the border of the next piece frame
	def createNextPieceArea(self):
		rowspan = max(0, int(self.nextBlockFrameHeightLen / self.gridWidth) - 2)
		colspan = max(0, int(self.rightFrameWidth / self.gridWidth) - 2)

		self.mainNextBlockFrame.grid(row = self.minRow + 1, column = self.minCol + 1,
		                             rowspan = rowspan,
									 columnspan = colspan,
									 sticky = 'W')

		self.mainNextBlockCanvas = Canvas(self.mainNextBlockFrame,
		                                  height = rowspan * self.gridWidth,
										  width = colspan * self.gridWidth,
										  bg = 'black')


		self.mainNextBlockCanvas.config(highlightthickness = 0)
		self.mainNextBlockCanvas.create_text(self.gridWidth * 3, self.gridWidth * 2, fill = "white", text = "Next Piece:", font=("Helvetica", 10))

		self.mainNextBlockCanvas.place(x = 0, y = 0)

	def drawGridToSubFrame(self, parentFrame, xLimit, yLimit):
		# Make function here
		self.canvasTetrisBorder = Canvas(parentFrame, height = yLimit,
	                                     width = xLimit, bg = 'gray71')
		# https://stackoverflow.com/questions/4310489/how-do-i-remove-the-light-grey-border-around-my-canvas-widget
		self.canvasTetrisBorder.config(highlightthickness = 0)
		self.drawGrid(self.canvasTetrisBorder, xLimit = xLimit, yLimit = yLimit)
		self.canvasTetrisBorder.place(x = 0, y = 0)

	# Function to create the content within the border of the window
	def createTetrisPlayArea(self):

		# Tetris area full height and width (including outline)
		xLimit = self.tetrisWidth + 2 * self.gridWidth
		yLimit = self.tetrisHeight + 2 * self.gridWidth

		# Tetris Parent Frame
		tetrisParent = Frame(self.mainFrame, height = yLimit, width = xLimit, bg = 'orange')
		tetrisParent.grid(row = self.minRow + 1, column = self.minCol + 1,
		                  rowspan = self.numberRows - 2, sticky = 'W')

		self.drawGridToSubFrame(parentFrame = tetrisParent, xLimit = xLimit, yLimit = yLimit)

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
		self.nextBlockFrame = Frame(rightFrame, bg = 'white',
		                            height = self.nextBlockFrameHeightLen,
		                            width = self.rightFrameWidth)
		self.nextBlockFrame.place(x = self.gridWidth,
		                          y = self.nextBlockFramePlaceY)

		self.mainNextBlockFrame = Frame(self.nextBlockFrame,
		                                height = self.nextBlockFrameHeightLen - 2 * self.gridWidth,
										width = self.rightFrameWidth - 2 * self.gridWidth,
										bg ='Red')
		nextBlockBorder = BorderedFrame(self.nextBlockFrame,
		                                self.gridWidth,
										self.rightFrameWidth,
										self.nextBlockFrameHeightLen,
										self.createNextPieceArea,
										'SeaGreen1')

		nextBlockBorder.addBorderSouthEast()

		# Start / Pause Button
		# .place() command parameters: http://effbot.org/tkinterbook/place.htm
		totH = self.labelFrameHeightLen * 2 + 2 * self.gridWidth
		startFrame = Frame(rightFrame, bg = 'black', height = totH,
						   width = self.windowWidth - self.tetrisWidth - 6 * self.gridWidth)

		# Restart / Settings button
		self.settingsRestartStr = StringVar()
		self.settingsRestartStr.set('Settings')
		self.restartButton = Button(startFrame, textvariable = self.settingsRestartStr, command = self.clickRestartButton)
		self.restartButton.config(font=("Helvetica", 10))
		self.restartButton.place(relx=0.5, rely=0.375, relwidth=1, relheight = self.labelFrameHeightLen/totH, anchor=CENTER)


		self.startButton = Button(startFrame, text = "Start /Pause Game", command = self.clickStartButton)
		self.startButton.config(font=("Helvetica", 10))
		self.startButton.place(relx=0.5, rely=1-0.125, relwidth=1, relheight=self.labelFrameHeightLen/totH, anchor=CENTER)
		#startFrame.place(x = self.gridWidth, y = self.startFramePlaceY)
		startFrame.place(x = self.gridWidth, y = self.startFramePlaceY - 2 * self.gridWidth - 2 *self.labelFrameHeightLen)

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
			newValueStrFull = ''.join([''.join('0' for idx in
	                          range(valueMaxLength - len(newValueStr))), newValueStr])
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

	# Color the grid cell in the specified location
	def colorCell(self, xCoord, yCoord, color, canvas):
		canvas.create_rectangle(xCoord * self.gridWidth, yCoord * self.gridWidth,
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
			self.colorCell(xCoord, yCoord, color, self.canvasTetris)

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
		factorTilt = random.choice(range(-self.numberRowsTetris + 1,
	                                      self.numberRowsTetris - 1))
		# Randomly initialise the speed of the loading screen
		speedInit = random.randint(5, 500) / 1000
		while (self.game.loading):
			# Increment the loop while alive
			idxRowBase = idxRowBase + 1
			# Don't allow the row index to exceed 19
			idxRowBase = idxRowBase % self.numberRowsTetris
			# speed = speedInit * math.sin(math.pi * (idxBase / 19))
			time.sleep(speedInit)
			for idxColor, color in enumerate(TetrisPiece.allColours):
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
			if self.game.loading: self.root.update(), print('update')
		self.clearLoadingScreen()

	# Dictate what happens when the start button is clicked
	def clickStartButton(self):
		self.game.loading = not self.game.loading
		if self.game.loading:
			self.settingsRestartStr.set('Settings')
		else:
			self.settingsRestartStr.set('Restart')

	# Dictate what happens when the restart button is pressed
	def clickRestartButton(self):
		if not self.game.loading:
			# Press restart button
			self.game.restart = True
		else:
			self.settingsWindow()

	def storeAndQuit(self):
		self.game.settings.difficulty = self.difficultyDisplay.get()
		self.newWindow.destroy()

	def settingsWindow(self):
		# Input main root to create the new window
		self.newWindow = Toplevel(self.root)
		self.newWindow.title('Settings')

		self.newWindow.geometry('{}x{}+{}+{}'.format(200,240,30,30))

		self.difficultyDisplay = IntVar(self.newWindow, self.game.settings.difficulty)

		# https://www.python-course.eu/tkinter_radiobuttons.php
		Label(self.newWindow,
		        text = """Select a Difficulty:""",
		        justify = LEFT,
		        padx = 20).pack(pady = 5)

		# Data input for radio buttons
		buttonData = [["Easy", self.game.settings.DIFFICULTY_EASY],
					  ["Intermediate", self.game.settings.DIFFICULTY_INT],
					  ["Hard", self.game.settings.DIFFICULTY_HARD]]

	    # Radiobuttons
		radioButtons = []
		for idx in range(3):
			radioButtons.append(Radiobutton(self.newWindow,
											text = buttonData[idx][0],
											indicatoron = False,
											relief = FLAT,
											borderwidth = 1,
											width = 20,
											pady = 10,
											padx = 20,
											variable = self.difficultyDisplay,
											value = buttonData[idx][1]).pack(pady = 5))
		# Save button
		exitSettings = Button(self.newWindow,
							  text = 'Save',
							  width = 10,
							  command = self.storeAndQuit).pack(pady = 10)

	    # When re-opening the window, the correct radio button should be marked
		selectedRadioButton = radioButtons[self.game.difficultyDisplay.get() - 1]
		selectedRadioButton.select()

	# Render empty screen
	def renderEmptyScreen(self):
		for idxRow in range(self.numberRowsTetris):
			for idxCol in range(self.numberColsTetris):
				self.colorCell(idxCol, idxRow, 'black', self.canvasTetris)

	# Render the next piece to the right of the playing area
	def renderNextPiece(self):

		numCols = 6
		numRows = 9

		# Clear previous colouring
		for idxRow in range(numRows):
			for idxCol in range(numCols):
				# Colour cell based on colour of next piece
				self.colorCell(idxCol, idxRow,
							   'black',
								self.mainNextBlockCanvas)
		# Add new colouring
		for idxRow in range(numRows):

			maxCol = self.game.nextPiece.getPieceMaxCol(returnGlobal = False)
			minCol = self.game.nextPiece.getPieceMinCol(returnGlobal = False)

			# Number of populated columns of the piece
			length = maxCol - minCol + 1
			# Half of the width of the piece
			inner = length / 2
			colLeftCentre = (numCols / 2 - 1)
			#
			colOffset = colLeftCentre - (inner - 1)


			for idxCol in range(maxCol + 1):
				if (idxRow <= len(self.game.nextPiece.value) - 1 and
				   idxCol <= len(self.game.nextPiece.value[0]) - 1 and
				   self.game.nextPiece.value[idxRow][idxCol] == 1):
				   # Colour cell based on colour of next piece
				   self.colorCell(idxCol + colOffset - minCol, idxRow + 4,
				                  self.game.nextPiece.colour,
								  self.mainNextBlockCanvas)

			self.mainNextBlockCanvas.create_text(self.gridWidth * 3, self.gridWidth * 2, fill = "white", text = "Next Piece:", font=("Helvetica", 10))

	# Function to render the piece on the screen
	def renderPieceOnScreen(self, fix):
		# Reset the rendering of previous piece to black
		if self.game.renderList:
			for point in self.game.renderList:
				# Point is (Row, Col), i.e. (Y, X)
				self.colorCell(point[1], point[0], 'black', self.canvasTetris)

		# Render the block's new position
		self.game.renderList = []
		(offsetRows, offsetCols) = self.game.currentPiece.position
		for idxRow, row in enumerate(self.game.currentPiece.value):
			for idxCol, value in enumerate(row):
				if value == 1:
					# Remember that we are rendering these indices of the grid
					if not fix:
						self.game.renderList.append((offsetRows + idxRow, offsetCols + idxCol))
					self.colorCell(offsetCols + idxCol, offsetRows + idxRow,
					               self.game.currentPiece.colour, self.canvasTetris)
		# Update the canvas each time the piece position changes
		self.root.update()

	# Render the fixed objects on the screen
	def renderObstaclesOnScreen(self):
		# Once rows have been removed, render the obstacles on the screen

		for idxRow, row in enumerate(self.game.obstacleGroup.value):
			for idxCol, dct in enumerate(row):
				if True in dct.keys():
					self.colorCell(idxCol, idxRow, dct[True], self.canvasTetris)
				else:
					self.colorCell(idxCol, idxRow, 'black', self.canvasTetris)
