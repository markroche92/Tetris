from tkinter import *
import copy
import time
import datetime
import math
import curses
import pickle
import os
from DisplayArea import DisplayType
from ObstacleGroup import ObstacleGroup
from TetrisPiece import TetrisPiece, PieceSet
from Settings import Settings
import numpy as np
from Utilities import log

class TetrisGame:
    # Max game level
    MAX_LEVEL =  1000
    MAX_SCORE = MAX_LEVEL * 1000
    lowLevelThreshold = 3
    midLevelThreshold = 6
    pickleName = 'leaderboard.pickle'

    def __init__(self, settings = None):

        ###################################################################
        ######################## Game Parameters ##########################
        ###################################################################

        # Parameter initialisation
        self.score = 0
        self.level = 1
        self.alive = True
        self.loading = True
        self.restart = False
        self.playerName = ''
        self.loadedData = None
        if settings:
            self.settings = copy.deepcopy(settings)
        else:
            self.settings = Settings()

        self.currentPiece, self.nextPiece = None, None
        self.paused = False # Flag goes True if pausing mid-game
        self.renderList = []
        self.renderListNext = []

    # Load past game data from pickle file
    def loadData(self):
        # Pickle is present, load it
        openedFile = open(self.pickleName, 'rb')
        # Decode information
        self.loadedData = pickle.load(openedFile, encoding='bytes')
        # Close file
        openedFile.close()

    # Check if pickle file exists
    def pickleExists(self):
        return self.pickleName in os.listdir(os.getcwd())

    # Save player name, score and time to .pickle
    def saveData(self):
        # Player name, score, date and time recorded
        newData = (self.playerName, self.score,
                   self.settings.difficulty, datetime.datetime.now())
        # Load in previous record
        if self.pickleName in os.listdir(os.getcwd()):
            # Load data
            self.loadData()
            # Add the data to list
            self.loadedData.append(newData)
        else:
            # Create a pickle
            self.loadedData = [newData]

        # Save the pickle
        outFile = open(self.pickleName,'wb')
        pickle.dump(self.loadedData, outFile)
        outFile.close()

    def setDisplayArea(self, displayArea):

        # Note the DisplayArea object which the game uses
        self.displayArea = displayArea

        # obstacleArray:
        # Each sublist represents a row of the tetris grid
        # Each element in the sublist represents a cell in the row
        # First sublist represents the top of the tetris grid
        # Dictionary is Boolean : String. Boolean: Is the cell occupied?  String: What is the color of the occupying block
        # Work with this variable as obstacleArray[row (0 based)][column (0 based)]
        self.obstacleGroup = ObstacleGroup(width = self.displayArea.numberColsTetris,
                                           height = self.displayArea.numberRowsTetris)

    # Generate a random block of random color
    def spawnBlock(self):

        if(self.level < self.lowLevelThreshold):
            pieceSet = PieceSet.TETRAMINO
        elif(self.level >= self.lowLevelThreshold and
             self.level <= self.midLevelThreshold):
            pieceSet = PieceSet.QUADRAMINO
        else:
            pieceSet = PieceSet.SEXTAMINO

        # Choose a block from dictionary
        if self.nextPiece:
        	self.currentPiece = copy.deepcopy(self.nextPiece)
        else:
        	self.currentPiece = TetrisPiece(pieceSet = pieceSet)
        self.nextPiece = TetrisPiece(pieceSet = pieceSet)

    # Update the position of the current piece under player control
    @log
    def gravity(self):
        # Create a copy of the current piece position, and increment column by 1 if possible
        copyPiece = copy.deepcopy(self.currentPiece)
        copyPiece.position[0] = min(self.displayArea.numberRowsTetris,
                                    copyPiece.position[0] + 1)
        # Get sets of obstacle and current piece indices
        copyPieceIndices = set(copyPiece.getPieceGlobalIndices())
        obstacleIndices = set(self.obstacleGroup.getObstacleIndices())

        # If gravity has caused the minimum row to be reached, or if gravity
        # has caused a collision with obstacles
        if (copyPiece.getPieceMaxRow() > self.displayArea.numberRowsTetris - 1 or
            set.intersection(obstacleIndices, copyPieceIndices)):

            # Fix = True - fix the position of the piece...
            fixRectangleList = self.displayArea.renderPieceOnScreen(fix = True)

            # Add the current piece to thee obstacle gorup
            self.obstacleGroup.addToGroup(self.currentPiece, fixRectangleList)
            # Need to spawn a new current piece
            self.currentPiece = None
        else:
        	# Update the position of the block base on the action of gravity
        	# Update ROW
        	self.currentPiece.position[0] = min(self.displayArea.numberRowsTetris,
        	                                    self.currentPiece.position[0] + 1)
            # Render the updated position of the current piece
            # Fix = False - no need to fix piece, as still under control
        	self.displayArea.renderPieceOnScreen(fix = False)

        ###################################################################
        ###################################################################

    # Run loop where user input is processed
    @log
    def userInput(self):
        # Measure the initial time
        timeInit = time.clock()
        curTime = timeInit
        cnt = 0

        if self.level <= 10:
            timeAllowedForMove = max(0.1, 0.5 - math.floor(self.level / 2) / 4 * 0.1)
        else:
            timeAllowedForMove = max(0.05, 0.1 - 0.05 * (self.level - 10) / 20)

        # Allow user inputs for a certain period of timeMax
        while(curTime - timeInit < timeAllowedForMove):
            curTime = time.clock()
            cnt = cnt + 1
            key = self.displayArea.cursesWindow.getch()
            #self.cursesWindow.addstr(str(time.clock() - timeInit) + " ")
            # If there is a use input
            if key != -1:
                obstacleIndices = set(self.obstacleGroup.getObstacleIndices())
            if key == ord('d'):

                rotatedPiece = TetrisPiece(pieceValue = self.currentPiece.clockwiseRotation(),
                    piecePosition = self.currentPiece.position,
                    pieceColour = self.currentPiece.colour)

                rotatedIndices = set(rotatedPiece.getPieceGlobalIndices())

                if (rotatedPiece.getPieceMinCol() > -1 and
                    rotatedPiece.getPieceMaxCol() < self.displayArea.numberColsTetris and
                    rotatedPiece.getPieceMaxRow() < self.displayArea.numberRowsTetris and
                    not set.intersection(rotatedIndices, obstacleIndices)):

                    self.currentPiece.value = self.currentPiece.clockwiseRotation()
                    # Call each time a key entry detected. Therefore, screen updated with each key press
                    self.displayArea.renderPieceOnScreen(fix = False)
                    #break
                    #self.root.update()
            elif key == ord('a'):
                rotatedPiece = TetrisPiece(pieceValue = self.currentPiece.counterClockwiseRotation(), piecePosition = self.currentPiece.position, pieceColour = self.currentPiece.colour)

                rotatedIndices = set(rotatedPiece.getPieceGlobalIndices())

                if (rotatedPiece.getPieceMinCol() > -1 and
                    rotatedPiece.getPieceMaxCol() < self.displayArea.numberColsTetris and
                    rotatedPiece.getPieceMaxRow() < self.displayArea.numberRowsTetris and
                    not set.intersection(rotatedIndices, obstacleIndices)):
                    #self.cursesWindow.addstr('GOT KEY A')
                    self.currentPiece.value = self.currentPiece.counterClockwiseRotation()
                    # Call each time a key entry detected. Therefore, screen updated with each key press
                    self.displayArea.renderPieceOnScreen(fix = False)
                    #break
                    #self.root.update()
            elif (key == curses.KEY_LEFT and
        	     self.currentPiece.getPieceMinCol() > 0):
                #self.cursesWindow.addstr('MOVE LEFT')

                copyPiece = copy.deepcopy(self.currentPiece)
                copyPiece.position[1] = copyPiece.position[1] - 1
                copyPieceIndices = set(copyPiece.getPieceGlobalIndices())

                if not set.intersection(copyPieceIndices, obstacleIndices):
                    minInnerCol = min(np.where(self.currentPiece.value == 1)[1])
                    self.currentPiece.position[1] = max(-minInnerCol,
                                                self.currentPiece.position[1] - 1)
                    # Call each time a key entry detected. Therefore, screen updated with each key press
                    self.displayArea.renderPieceOnScreen(fix = False)
                #break
            elif (key == curses.KEY_RIGHT and
        	     self.currentPiece.getPieceMaxCol() < self.displayArea.numberColsTetris - 1):

                copyPiece = copy.deepcopy(self.currentPiece)
                copyPiece.position[1] = copyPiece.position[1] + 1
                copyPieceIndices = set(copyPiece.getPieceGlobalIndices())

                if not set.intersection(copyPieceIndices, obstacleIndices):
                    #self.cursesWindow.addstr('MOVE RIGHT')
                    self.currentPiece.position[1] = min(self.displayArea.numberColsTetris,
                                                    self.currentPiece.position[1] + 1)
                    # Call each time a key entry detected. Therefore, screen updated with each key press
                    self.displayArea.renderPieceOnScreen(fix = False)
            elif (key == curses.KEY_DOWN and
            self.currentPiece.getPieceMaxRow() < self.displayArea.numberRowsTetris - 1):

                copyPiece = copy.deepcopy(self.currentPiece)
                copyPiece.position[0] = copyPiece.position[0] + 1
                copyPieceIndices = set(copyPiece.getPieceGlobalIndices())

                if not set.intersection(copyPieceIndices, obstacleIndices):
                #self.cursesWindow.addstr('MOVE RIGHT')
                    self.currentPiece.position[0] = min(self.displayArea.numberRowsTetris,
                                            self.currentPiece.position[0] + 1)
                    # Call each time a key entry detected. Therefore, screen updated with each key press
                    self.displayArea.renderPieceOnScreen(fix = False)

            elif (key == curses.KEY_UP and
            self.currentPiece.getPieceMaxRow() < self.displayArea.numberRowsTetris - 1):
                copyPiece = copy.deepcopy(self.currentPiece)
                occupiedPoints = copyPiece.getPieceGlobalIndices()
                # Create list of lowest points in grid which are populated by the piece
                lowestInOccupiedCols = []
                for point in occupiedPoints:
                    if point[1] not in set([p[1] for p in lowestInOccupiedCols]):
                        lowestInOccupiedCols.append(point)
                    else:
                        for p in lowestInOccupiedCols:
                            if point[1] == p[1]:
                                if point[0] > p[0]:
                                    lowestInOccupiedCols.remove(p)
                                    lowestInOccupiedCols.append(point)

                closestObstacle = None
                inc = 1
                searching = [True]
                while((not closestObstacle) and
                      (not False in searching)):
                    searching = []
                    for point in lowestInOccupiedCols:
                        col = point[1]
                        rowNew = point[0] + inc
                        if rowNew > self.displayArea.numberRowsTetris - 1:
                            searching.append(False)
                        else:
                            if True in self.obstacleGroup.value[rowNew][col].keys():
                                searching.append(False)
                                closestObstacle = [rowNew, col]
                                break
                            else:
                                searching.append(True)
                    inc = inc + 1


                copyPiece.position[0] = copyPiece.position[0] + inc - 2
                copyPieceIndices = set(copyPiece.getPieceGlobalIndices())

                if not set.intersection(copyPieceIndices, obstacleIndices):
                #self.cursesWindow.addstr('MOVE RIGHT')
                    pieceHeight = self.currentPiece.getPieceMaxRow() - self.currentPiece.getPieceMinRow() + 1
                    self.currentPiece.position[0] = min(self.displayArea.numberRowsTetris - pieceHeight,
                        self.currentPiece.position[0] + inc - 2)
                    # Call each time a key entry detected. Therefore, screen updated with each key press
                    self.displayArea.renderPieceOnScreen(fix = False)

    # Remove any rows which are now complete
    def removeRows(self):
        doRemove = False
        # Count the number of rows to be removed
        countRowsRemoved = sum([1 if self.obstacleGroup.checkRow(idx) else 0
                                for idx, row in enumerate(self.obstacleGroup.value)])
        # Score increase is poroportional to square of number of rows to remove
        bonus = countRowsRemoved * countRowsRemoved * 100

        if countRowsRemoved > 0: self.displayArea.hideTetris(remove = True)

        for idxRow in range(self.displayArea.numberRowsTetris):
            if self.obstacleGroup.checkRow(idxRow):
                doRemove = True

                self.obstacleGroup.removeRow(idxRow)
                self.score = self.score + math.floor(bonus / countRowsRemoved)
                self.displayArea.updateDisplay(self.score, DisplayType.SCORE)
                if (self.score != 0 and self.level < self.MAX_LEVEL):
                    # Increment the level each time the scoroe
                    levelPrev = copy.deepcopy(self.level)
                    self.level = math.floor(self.score / 1000)
                    if levelPrev != self.level: self.displayArea.updateDisplay(self.level, DisplayType.LEVEL)
        if doRemove: self.displayArea.renderObstaclesOnScreen()
