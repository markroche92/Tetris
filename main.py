from tkinter import *
from math import floor
from enum import Enum

class DisplayType(Enum):
	SCORE = 0
	LEVEL = 1

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

	def __init__(self, root):

		# Set up the window and borders for display
		self.alive = True
		self.root = root

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
		                          width = self.windowWidth - self.gridWidth, bg = 'green')
		windowBorderWest = Frame(self.mainFrame, height = self.windowHeight - self.gridWidth,
		                         width = self.gridWidth, bg = 'green')
		windowBorderSouth = Frame(self.mainFrame, height = self.gridWidth,
		                          width = self.windowWidth  - self.gridWidth, bg = 'green')
		windowBorderEast = Frame(self.mainFrame, height = self.windowHeight  - self.gridWidth,
		                         width = self.gridWidth, bg = 'green')

	 	# Window Border Placement
		windowBorderNorth.grid(row = self.minRow, column = self.minCol,
		                       columnspan = self.numberCols - 1, sticky = 'N')
		windowBorderWest.grid(row = self.minRow + 1, column = self.minCol,
		                      rowspan = self.numberRows - 1, sticky = 'W')
		# Tetris Parent Frame
		tetrisParent = Frame(self.mainFrame, height = self.tetrisHeight + 2 * self.gridWidth,
		                     width = self.tetrisWidth + 2 * self.gridWidth, bg = 'orange')
		tetrisParent.grid(row = self.minRow + 1, column = self.minCol + 1,
		                  rowspan = self.numberRows - 2, sticky = 'W')

		# Tetris Frame
		tetrisFrame = Frame(tetrisParent, height = self.tetrisHeight,
		                     width = self.tetrisWidth, bg = 'black')
		tetrisFrame.place(x = self.gridWidth, y = self.gridWidth)

		# Left Frame
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
		startButton = Button(startFrame, text = "Start /Pause Game")
		startButton.config(font=("Helvetica", 10))
		startButton.place(relx=0.5, rely=0.5, relwidth=1, relheight=1, anchor=CENTER)
		startFrame.place(x = self.gridWidth, y = self.startFramePlaceY)

		# Window Borders South and East
		windowBorderSouth.grid(column = self.minCol + 1, row = self.maxRow,
		                       columnspan = self.numberCols - 1, sticky = 'S')
		windowBorderEast.grid(row = self.minRow, column = self.maxCol,
		                      rowspan = self.numberRows - 1, sticky = 'E')

	    ###################################################################
		###################################################################


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


root = Tk()
Game = TetrisGame(root = root)

# Run program until window closed
score, level = 0, 0
while (Game.alive):
	score = score + 100
	level = floor(score / 1000000)
	# Update the Score
	Game.updateDisplay(score, DisplayType.SCORE)
	# Update the level
	Game.updateDisplay(level, DisplayType.LEVEL)

	if Game.alive: root.update()
