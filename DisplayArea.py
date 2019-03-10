from BorderedFrame import BorderedFrame
from tkinter import *
from math import floor
from enum import Enum
import numpy as np
import random
import time
from TetrisPiece import TetrisPiece
import curses
from Utilities import log

# Window placement, dimensions and properties
def setRootProperties(root, windowHeight, windowWidth, background = 'black',
                            title = 'Tetris Application'):
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

    # Number of digits in the score / level number
    scoreNumberDigits, levelNumberDigits = 6, 3

    # Score Pre-String
    scoreBaseStr = "Score:"
    # Level Pre-String
    levelBaseStr = "Level:"
    # Next Piece StringVar
    nextPieceStr = 'Next Piece:'

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
    #numberColsNextPiece, numberRowsNextPiece = 6, 9
    numberRowsTetris, numberColsTetris = (int(tetrisHeight / gridWidth),
                                          int(tetrisWidth / gridWidth))

    # Calculate the length allowed for the next block frame
    nextBlockFrameHeightLen = (windowHeight - 4 * labelFrameHeightLen -
    					   	   gridWidth * 9)

    # Width for the the right frame
    rightFrameWidth = (windowWidth - tetrisWidth - 6 * gridWidth)

    numberRowsNextPiece = max(0, int(nextBlockFrameHeightLen / gridWidth) - 2)
    numberColsNextPiece = max(0, int(rightFrameWidth / gridWidth) - 2)

    # Placement of frames on Y axis
    # Note: These measurements are taken from the base of rightFrame
    scoreFramePlaceY = gridWidth
    levelFramePlaceY = 2 * gridWidth + labelFrameHeightLen
    nextBlockFramePlaceY = gridWidth * 3 + 2 * labelFrameHeightLen
    startFramePlaceY = windowHeight - gridWidth * 3 - labelFrameHeightLen

    def __init__(self, root, cursesWindow, gameObject):

    	# Set up the window and borders for display
    	self.game = gameObject
    	self.root = root
    	self.cursesWindow = cursesWindow
    	self.cursesWindow.nodelay(1)

    	# Initialise the Score Sting
    	self.scoreString = StringVar()
    	self.scoreString.set('{} {}'.format(self.scoreBaseStr,
    	                     ''.join(['0' for x in range(self.scoreNumberDigits)])))

    	# Initialise the Score Sting
    	self.levelString = StringVar()
    	self.levelString.set('{} {}'.format(self.levelBaseStr,
    	                     ''.join(['0' for x in range(self.levelNumberDigits)])))

    	# Initialise the Start Button text
    	self.startString = StringVar()
    	self.startString.set('Start')

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

    # Color the grid cell in the specified location
    def colorCell(self, xCoord, yCoord, color, canvas):
    	# Return the rectangle which has been coloured on the canvas
    	return canvas.create_rectangle(xCoord * self.gridWidth,
    								   yCoord * self.gridWidth,
    	                               (xCoord + 1) * self.gridWidth,
    								   (yCoord + 1) * self.gridWidth,
    								   fill = color)

    # Function to create content within the border of the next piece frame
    def createNextPieceArea(self):

    	# Allow space for border (+ 1)
    	self.mainNextBlockFrame.grid(row = self.minRow + 1, column = self.minCol + 1,
    	                             rowspan = self.numberRowsNextPiece,
    								 columnspan = self.numberColsNextPiece,
    								 sticky = 'W')

    	# Canvas colour is default black, so no need to create_rectangle('black')
    	self.mainNextBlockCanvas = Canvas(self.mainNextBlockFrame,
    	                                  height = self.numberRowsNextPiece * self.gridWidth,
    									  width = self.numberColsNextPiece * self.gridWidth,
    									  bg = 'black')

    	# Presentation
    	self.mainNextBlockCanvas.config(highlightthickness = 0)

    	# Default the next piece label to white
    	self.nextPieceLabel = self.mainNextBlockCanvas.create_text(self.gridWidth * 3,
    										self.gridWidth * 2,
    										fill = "white",
    										text = "Next Piece:",
    										font=("Helvetica", 10))

    	# Place canvas
    	self.mainNextBlockCanvas.place(x = 0, y = 0)

    # Dictate what happens when the start button is clicked
    def clickStartButton(self):
    	# If a player name has already been set
    	if not self.game.playerName:
    		# If the name field is empty, and a name has not already been recorded
    		if not self.nameEnteredStr.get():
    			for x in range(1):
    				time.sleep(0.25)
    				self.nameLabel.config(fg = 'red')
    				self.root.update()
    				time.sleep(0.25)
    				self.nameLabel.config(fg = 'white')
    				self.root.update()
    			return
    		else:
    			# Set the player name, if the field is non-empty
    			self.game.playerName = self.nameEnteredStr.get()

    	self.game.loading = not self.game.loading
    	# Change the button text depending on the game state
    	if self.game.loading:
    		self.settingsRestartStr.set('Settings')
    		self.startString.set('Start')
    		self.leaderboardButtton.config(bg = 'white', borderwidth = 1)
    	else:
    		self.settingsRestartStr.set('Restart')
    		self.startString.set('Pause')
    		self.nameLabelStr.set('Playing As:')
    		self.nameField.config(state = DISABLED)
    		self.leaderboardButtton.config(bg = 'black', borderwidth = 0)

    # Dictate what happens when the restart button is pressed
    def clickRestartButton(self):
    	if not self.game.loading:
    		# Press restart button
    		self.game.restart = True
    	else:
    		# Restart Button opens settings window once in the loading screen
    		self.settingsWindow()

    # Dictate what happens when the leaderboard button is processed
    def clickLeaderboardButton(self):
        # Button only responds if the game is in the loading state
        if self.game.loading and self.game.pickleExists():
            # Input main root to create the new window
            self.newWindow = Toplevel(self.root, bg = 'black')
            # Title the leaderboard window
            self.newWindow.title('Leaderboard')
            # Load from pickle, if data has not alrready been loaded
            if not self.game.loadedData: self.game.loadData()

            # List of listes - splitting data based on playing difficulty
            topGameList = [[o for o in self.game.loadedData if
                            o[2] == self.game.settings.DIFFICULTY_EASY],
                            [o for o in self.game.loadedData if
                            o[2] == self.game.settings.DIFFICULTY_INT],
                            [o for o in self.game.loadedData if
                            o[2] == self.game.settings.DIFFICULTY_HARD]]


            for sublist in topGameList:
                # Sort based on score
                sublist.sort(key = lambda x: x[1])
                sublist.reverse()

            for idx, difficulty in enumerate(self.game.settings.difficulties):
                diffString = self.game.settings.difficultiesString[idx]
                # Select the results list based on the difficulty
                gameList = topGameList[idx]
                for i in range(11): #Rows
                    if i == 0 and gameList:
                        title = Label(self.newWindow,
                        text = 'Top 10 play ranking ' +
                        'for difficulty level: ' + diffString,
                        font = "Helvetica 10 bold", bg = 'black', fg = 'white')
                        title.grid(row = i, column = 4 * idx, columnspan = 4)

                        for idxHeader, headerText in enumerate(['Player Name',
                                                                'Score',
                                                                'Date & Time']):
                            header = Label(self.newWindow,
                            text = headerText,
                            font = "Helvetica 10 bold", bg = 'black', fg = 'white')
                            header.grid(row = 1, column = idxHeader + 4 * idx + 1)
                    else:
                        # If there are still logged plays for this difficulty level
                        if gameList:
                            data = gameList.pop(0)
                            dateT = data[3]
                            data = [data[0],
                                    data[1],
                                    '{}/{}/{} {}:{}:{}'.format(dateT.day,
                                                            dateT.month,
                                                            dateT.year,
                                                            dateT.hour,
                                                            dateT.minute,
                                                            dateT.second)]
                            for j in range(4): #Columns
                                # Print Name, Score, Date/Time
                                if j == 0:
                                    Label(self.newWindow,
                                          text = str(i) + '.  ', bg = 'black',
                                                 fg = 'white').grid(row = i + 1,
                                                 column = idx * 4)
                                else:
                                    stringData = StringVar()
                                    stringData.set(data[j - 1])
                                    entry = Entry(self.newWindow,
                                            textvariable = stringData,
                                            bg = 'black', fg = 'white')
                                    entry.grid(row=i + 1, column=j + idx * 4,
                                                padx = 5, pady = 5)
                                    entry.config(state = DISABLED)

    # Functionality and design of settings window
    def settingsWindow(self):

    	def storeAndQuit(display):
    		display.game.settings.difficulty = display.difficultyDisplay.get()
    		display.newWindow.destroy()

    	# Input main root to create the new window
    	self.newWindow = Toplevel(self.root)
    	self.newWindow.title('Settings')
    	self.newWindow.geometry('{}x{}+{}+{}'.format(200,240,30,30))

    	self.difficultyDisplay = IntVar(self.newWindow, self.game.settings.difficulty)

    	# https://www.python-course.eu/tkinter_radiobuttons.php
    	# Define text, and pack to the window
    	Label(self.newWindow,
    	        text = "Select a Difficulty:",
    	        justify = LEFT,
    	        padx = 20).pack(pady = 5)

    	# Data input for radio buttons
    	buttonData = [["Easy", self.game.settings.DIFFICULTY_EASY],
    				  ["Intermediate", self.game.settings.DIFFICULTY_INT],
    				  ["Hard", self.game.settings.DIFFICULTY_HARD]]

        # Radiobuttons
    	radioButtons = []
    	for idx in range(len(buttonData)):
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
    						  command = lambda: storeAndQuit(self)).pack(pady = 10)

        # When re-opening the window, the correct radio button should be marked
    	#selectedRadioButton = radioButtons[self.game.settings.difficulty - 1]
    	#selectedRadioButton.select()

    # Render empty screen
    # Remove flag is set when rows are being removed from obstacle group
    def hideTetris(self, remove = False):
    	# Hiding obstacles when pausing and going to loading screen
    	# Obstacles can be deleted or just coloured black
    	for idxRow in range(self.numberRowsTetris):
    		for idxCol in range(self.numberColsTetris):
    			if True in self.game.obstacleGroup.value[idxRow][idxCol].keys():
    				rectangle = self.game.obstacleGroup.value[idxRow][idxCol][True][1]
    				if remove:
    					self.canvasTetris.delete(rectangle)
    				else:
    					self.canvasTetris.itemconfig(rectangle, fill='black')

    	if not remove:
    		for rectangle in self.game.renderList:
    			self.canvasTetris.itemconfig(rectangle, fill = 'black')

    # Render the fixed objects on the screen
    #@log
    def renderObstaclesOnScreen(self):
    	# Once rows have been removed, render the obstacles on the screen
    	for idxRow, row in enumerate(self.game.obstacleGroup.value):
    		for idxCol, dct in enumerate(row):
    			if True in dct.keys():
    				# Colour based on occupying block colour
    				# Set the rectangle value in teh dictionary
    				# [1] = rectangle object, [0] is colour string
    				dct[True][1] = self.colorCell(xCoord = idxCol,
    											  yCoord = idxRow,
    									  		  color = dct[True][0],
    											  canvas = self.canvasTetris)

    # Function to render the piece on the screen
    #@log
    def renderPieceOnScreen(self, fix):
    	# Reset the rendering of previous piece to black
    	for rectangle in self.game.renderList:
    		self.canvasTetris.delete(rectangle)

    	# Render the block's new position
    	# renderList stores the rectangles for thee current piece
    	self.game.renderList[:] = []

    	# This variable will hold the rectangles for the piece to be fixed into
    	# obstacle group, if fix = True is set
    	fixRectangleList = [[None,] * np.shape(self.game.currentPiece.value)[1]
    						for x in range(np.shape(self.game.currentPiece.value)[0])]

    	# Position offsets required for rendering on tetris grid
    	(offsetRows, offsetCols) = self.game.currentPiece.position

    	# Iterate across rows and cols of current piece
    	for idxRow, row in enumerate(self.game.currentPiece.value):
    		for idxCol, value in enumerate(row):
    			if value == 1:
    				# Remember that we are rendering these indices of the grid
    				if not fix:
    					# If not fixing to the obstacle group
    					# Hold in render list, until this function is next called
    					self.game.renderList.append(self.colorCell(offsetCols + idxCol,
    															   offsetRows + idxRow,
    					               							   self.game.currentPiece.colour,
    															   self.canvasTetris))
    				else:
    					# If fixing the current piece, this variable is to be returned
    					fixRectangleList[idxRow][idxCol] = self.colorCell(offsetCols + idxCol,
    					                                                  offsetRows + idxRow,
    					                                                  self.game.currentPiece.colour,
    																	  self.canvasTetris)
    	# Update the canvas each time the piece position changes
    	self.root.update()

    	if fix: return fixRectangleList

    # Function to create the content within the border of the window
    def createTetrisPlayArea(self):

    	def drawGridToSubFrame(self, parentFrame, xLimit, yLimit):

    	    # Return numpy array of x and y co-ordinates corresponding to a grid from (0,0)
    	    # to specified limit
    		def drawGrid(self, canvas, xLimit, yLimit):
    			# Get vectors of co-ordinates
    			xVector = np.linspace(0, xLimit, xLimit / self.gridWidth + 1)
    			yVector = np.linspace(0, yLimit, yLimit / self.gridWidth + 1)
    			# Draw grid
    			[canvas.create_line(xCoord, 0,
    								xCoord , self.tetrisHeight + 2 * self.gridWidth)
    								for xCoord in xVector]
    			[canvas.create_line(0, yCoord,
    								self.tetrisWidth + 2 * self.gridWidth, yCoord)
    								for yCoord in yVector]

    		# Make function here
    		self.canvasTetrisBorder = Canvas(parentFrame, height = yLimit,
    	                                     width = xLimit, bg = 'gray71')
    		# https://stackoverflow.com/questions/4310489/how-do-i-remove-the-light-grey-border-around-my-canvas-widget
    		self.canvasTetrisBorder.config(highlightthickness = 0)
    		drawGrid(self, self.canvasTetrisBorder, xLimit = xLimit, yLimit = yLimit)
    		self.canvasTetrisBorder.place(x = 0, y = 0)

    	# Tetris area full height and width (including outline)
    	xLimit = self.tetrisWidth + 2 * self.gridWidth
    	yLimit = self.tetrisHeight + 2 * self.gridWidth
    	totH = self.labelFrameHeightLen * 2 + 3 * self.gridWidth

    	# Tetris Parent Frame
    	tetrisParent = Frame(self.mainFrame, height = yLimit,
    	                     width = xLimit, bg = 'orange')
    	tetrisParent.grid(row = self.minRow + 1, column = self.minCol + 1,
    	                  rowspan = self.numberRows - 2, sticky = 'W')

    	drawGridToSubFrame(self = self, parentFrame = tetrisParent,
    	                        xLimit = xLimit, yLimit = yLimit)

    	# Tetris Frame
    	tetrisFrame = Frame(tetrisParent, height = self.tetrisHeight,
    	                     width = self.tetrisWidth, bg = 'black')
    	tetrisFrame.place(x = self.gridWidth, y = self.gridWidth)
    	self.canvasTetris = Canvas(tetrisFrame, height = yLimit,
    	                           width = xLimit, bg = 'black')
    	# https://stackoverflow.com/questions/4310489/how-do-i-remove-the-light-grey-border-around-my-canvas-widget
    	self.canvasTetris.config(highlightthickness = 0)
    	self.canvasTetris.place(x = 0, y = 0)


    	# Right Frame
    	rightFrame = Frame(self.mainFrame,
                   height = self.tetrisHeight + 2 * self.gridWidth,
                   width = self.windowWidth - self.tetrisWidth - 4 * self.gridWidth,
    			   bg = 'black')
    	rightFrame.grid(row = self.minRow + 1,
    	                column = 1 + self.numberColsTetris + 2,
    					sticky = 'W')

    	# Score
    	# .place() command parameters: http://effbot.org/tkinterbook/place.htm
    	scoreFrame = Frame(rightFrame, bg = 'black',
    	                   height = self.labelFrameHeightLen,
    	                   width = self.rightFrameWidth)
    	scoreLabel = Label(scoreFrame, textvariable = self.scoreString)
    	scoreLabel.config(font=("Helvetica", 10), fg = 'white', bg = 'black')
    	scoreLabel.place(relx = 0.5, rely = 0.5, relwidth=1, relheight=1,
    	                 anchor = CENTER)
    	scoreFrame.place(x = self.gridWidth , y = self.scoreFramePlaceY)

    	# Level
    	# .place() command parameters: http://effbot.org/tkinterbook/place.htm
    	levelFrame = Frame(rightFrame, bg = 'black',
    	                   height = self.labelFrameHeightLen,
    	                   width = self.rightFrameWidth)
    	levelLabel = Label(levelFrame, textvariable = self.levelString)
    	levelLabel.config(font=("Helvetica", 10), fg = 'white', bg = 'black')
    	levelLabel.place(relx=0.2, rely=0.5, relwidth=0.45, relheight=1,
    	                 anchor=CENTER)
    	levelFrame.place(x = self.gridWidth , y = self.levelFramePlaceY)

    	# Leaderboard
    	self.leaderboardButtton = Button(levelFrame, text = 'Leaders',
    	                                 command = self.clickLeaderboardButton)
    	self.leaderboardButtton.config(font=("Helvetica", 10))
    	self.leaderboardButtton.place(relx=0.8, rely=0.5, relwidth=0.45,
    	                       relheight=1,
    						   anchor=CENTER)


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
    	startFrame = Frame(rightFrame, bg = 'black', height = totH,
    					   width = self.windowWidth - self.tetrisWidth - 6 * self.gridWidth)

    	# Restart / Settings button
    	self.settingsRestartStr = StringVar()
    	self.settingsRestartStr.set('Settings')
    	self.restartButton = Button(startFrame,
    								textvariable = self.settingsRestartStr,
    								command = self.clickRestartButton)
    	self.restartButton.config(font=("Helvetica", 10))
    	self.restartButton.place(relx=0.2, rely=0.3, relwidth=0.45,
    	                         relheight = self.labelFrameHeightLen/totH,
    							 anchor=CENTER)


    	self.startButton = Button(startFrame, textvariable = self.startString,
    	                          command = self.clickStartButton)
    	self.startButton.config(font=("Helvetica", 10))
    	self.startButton.place(relx=0.8, rely=0.3, relwidth=0.45,
    	                       relheight=self.labelFrameHeightLen/totH,
    						   anchor=CENTER)

    	self.nameLabelStr = StringVar()
    	self.nameLabelStr.set('Enter Player Name:')
    	self.nameLabel = Label(startFrame, textvariable = self.nameLabelStr,
    	                       bg = 'black', fg = 'white', anchor = W)
    	self.nameLabel.place(relx=0, rely=0.6, relwidth=1,
    	                       relheight=self.labelFrameHeightLen/totH)

    	self.nameEnteredStr = StringVar()
    	self.nameField = Entry(startFrame, textvariable=self.nameEnteredStr)
    	self.nameField.place(relx=0, rely=0.8, relwidth=1,
    	                     relheight=self.labelFrameHeightLen/totH)

    	#startFrame.place(x = self.gridWidth, y = self.startFramePlaceY)
    	startFrame.place(x = self.gridWidth,
    	           y = self.startFramePlaceY - 2 * self.gridWidth - 2 *self.labelFrameHeightLen)

    # Just make the next piece invisible
    # retain = True if transitioning to loading menu for pause
    # retain = False if new piece is being generated
    def hideNextPiece(self, retain = False):
    	# Retain used if jumping to paused state
    	if retain: self.mainNextBlockCanvas.itemconfig(self.nextPieceLabel,
    	                                               fill = 'black')
    	for rectangle in self.game.renderListNext:
    		if retain:
    			# Just colour it black
    			self.mainNextBlockCanvas.itemconfig(rectangle, fill = 'black')
    		else:
    			# Remove from canvas
    			self.mainNextBlockCanvas.delete(rectangle)

    # Just make the next piece visible again, after colouring black
    def restoreNextPiece(self):
    	# Mke label visibla again
    	self.mainNextBlockCanvas.itemconfig(self.nextPieceLabel, fill = 'white')
    	for rectangle in self.game.renderListNext:
    		# Just colour it back to original colour
    		self.mainNextBlockCanvas.itemconfig(rectangle, fill = self.game.nextPiece.colour)

    # Display the loading screen to the player
    def runLoadingScreen(self):

        # When tetris border changes color, the game is paused
        self.canvasTetrisBorder.config(bg = 'gold')

        # Randomly initialise the tilt of the blocks shown on the loading screen
        factorTilt = random.choice(range(-self.numberRowsTetris + 1,
                                          self.numberRowsTetris - 1))

        # Randomly initialise the speed of the loading screen
        speedInit = random.randint(5, 500) / 1000

        # Initialise variables for while loop
        idxRowBase = 0
        prevLoadingRectangles = []

        while (self.game.loading):
            # Increment the loop while alive
            # Don't allow the row index to exceed 19
            idxRowBase = (idxRowBase + 1) % self.numberRowsTetris

            time.sleep(speedInit)
            if prevLoadingRectangles:
                for rectangle in prevLoadingRectangles:
                    if self.root: self.canvasTetris.delete(rectangle)

            # Empty the list
            # https://stackoverflow.com/questions/1400608/how-to-empty-a-list-in-python
            prevLoadingRectangles[:] = []


            for idxColor, color in enumerate(TetrisPiece.allColours):
                # Don't allow the processed row index exceed 19
                idxRowTilt = (idxRowBase + factorTilt * idxColor) % 20
                # Don't allow the processed previous row index exceed 19
                idxRowPrev = idxRowTilt - 1 if idxRowTilt != 0 else 19

                prevLoadingRectangles.append(self.colorCell(idxColor,
                				idxRowTilt,
                				color,
                				self.canvasTetris))

            # Flashing start button
            if idxRowBase % 10 < 5:
                self.startButton.config(bg='SeaGreen1')
            elif idxRowBase % 10 >= 5:
                self.startButton.config(bg='white')

            # Update the display as long as the game hasn't been closed
            if self.game.loading: self.root.update()
        # Delete any loading screen rectangles
        for rectangle in prevLoadingRectangles:
            self.canvasTetris.delete(rectangle)
        # Set tetris border colour back to grey
        self.canvasTetrisBorder.config(bg = 'gray71')

    # Update the score displayed or update the level displayed
    def updateDisplay(self, newValue, displayType):

    	if displayType is DisplayType.SCORE:
    		valueMaxLength = self.scoreNumberDigits
    	elif displayType is DisplayType.LEVEL:
    		valueMaxLength = self.levelNumberDigits
    	else:
    		self.alive = False
    		self.root.destroy()
    		raise Exception('''Unrecognised displayType ''{}'' in function
    		                   updateDisplay()'''.format(displayType))

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

    # Render the next piece to the right of the playing area
    def renderNextPiece(self):

    	# Clear the previous 'next piece' from the canvas
    	self.hideNextPiece()

    	# Clear the list now that they have been removed from the canvas
    	self.game.renderListNext[:] = []

    	# Add new colouring
    	for idxRow in range(self.numberRowsNextPiece):

    		maxCol = self.game.nextPiece.getPieceMaxCol(returnGlobal = False)
    		minCol = self.game.nextPiece.getPieceMinCol(returnGlobal = False)

    		# Number of populated columns of the piece
    		length = maxCol - minCol + 1
    		# Half of the width of the piece
    		inner = length / 2
    		# Column left of centre within the 'next piece area'
    		colLeftCentre = (self.numberColsNextPiece / 2 - 1)
    		# Column left of centring the piece in the 'next piece area'
    		colOffset = colLeftCentre - (inner - 1)

    		for idxCol in range(maxCol + 1):
    			# If within bounds, and there the cell is populated by the next piece
    			if (idxRow <= len(self.game.nextPiece.value) - 1 and
    			   idxCol <= len(self.game.nextPiece.value[0]) - 1 and
    			   self.game.nextPiece.value[idxRow][idxCol] == 1):
    			   # Colour cell based on colour of next piece
    			   self.game.renderListNext.append(self.colorCell(idxCol + colOffset - minCol,
    							   				  idxRow + 4,
    							                  self.game.nextPiece.colour,
    											  self.mainNextBlockCanvas))
