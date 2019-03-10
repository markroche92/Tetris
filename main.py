from tkinter import *
from math import floor
from TetrisPiece import TetrisPiece
from ObstacleGroup import ObstacleGroup
from BorderedFrame import BorderedFrame
from DisplayArea import DisplayArea
from TetrisGame import TetrisGame
from Utilities import log
import numpy as np
import curses
import sys
import os

def startGame(root, window, prevDisplay = None, settings = None):

	Game = TetrisGame(settings)
	if prevDisplay:
		Display = DisplayArea(root = prevDisplay.root,
							  cursesWindow = prevDisplay.cursesWindow,
							  gameObject = Game)
	else:
		Display = DisplayArea(root = root,
							  cursesWindow = window,
					  		  gameObject = Game)
	Game.setDisplayArea(displayArea = Display)
	return Game, Display

@log
def main(window):
	root = Tk()
	(Game, Display) = startGame(root, window)
	wasLoading, wasRunning = False, False
	while (Game.alive):
		if Game.restart:
			wasRunning, wasLoading = False, False
			root.destroy()
			root = Tk()
			Game, Display = startGame(root = root,
			                          window = window,
									  settings = Game.settings)
		elif Game.loading:
			#window.addstr('LOADING ')
			# Show loading screen until not loading
			# runLoadingScreen() contains a while() running at random speed
			# Note: Game.runLoadingScreen() contains root.update()

			# Change the colour of obstacles, current piece and next piece to black
			if not wasLoading: Display.hideTetris(), Display.hideNextPiece(retain = True)
			if wasRunning and not wasLoading:
				Game.paused = True
				#Display.restartButton.config(state = DISABLED)
				Display.startString.set("Resume")
			wasRunning, wasLoading = False, True


			# Run while loop, displaying loading screen
			Display.runLoadingScreen()
		else:
			# Re-render the obstacles on the screen if loading has been cancelled
			if wasLoading: Display.renderObstaclesOnScreen(), Display.restoreNextPiece()
			if wasLoading and not wasRunning:
				Game.paused = True
				#Display.restartButton.config(state = NORMAL)
				Display.startString.set("Pause")
			wasRunning, wasLoading = True, False

			if Game.currentPiece:
				Game.userInput()
				Game.gravity()
				Game.removeRows()
			elif(Game.obstacleGroup.getMaxRow()):
				print('GAME OVER!')
				print('Final Score: ', Game.score)
				Game.saveData()
				break
			else:
				Game.spawnBlock()
				Display.renderNextPiece()
		root.update()


if 'logging.txt' in os.listdir(os.getcwd()): os.remove("logging.txt")
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
