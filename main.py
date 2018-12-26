from tkinter import *
from math import floor
from TetrisPiece import TetrisPiece
from ObstacleGroup import ObstacleGroup
from BorderedFrame import BorderedFrame
from DisplayArea import DisplayArea
from TetrisGame import TetrisGame
import numpy as np
import curses
import sys

def startGame(root, window, prevDisplay = None):

	Game = TetrisGame()
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

def main(window):
	root = Tk()
	(Game, Display) = startGame(root, window)
	wasLoading = False
	while (Game.alive):
		if Game.restart:
			root.destroy()
			root = Tk()
			Game, Display = startGame(root = root,
			                          window = window)
		elif Game.loading:
			#window.addstr('LOADING ')
			# Show loading screen until not loading
			# runLoadingScreen() contains a while() running at random speed
			# Note: Game.runLoadingScreen() contains root.update()
			wasLoading = True
			if not wasLoading: Display.renderEmptyScreen()
			Display.runLoadingScreen()
		else:
			# Re-render the obstacles on the screen if loading has been cancelled
			if wasLoading: Display.renderObstaclesOnScreen()
			wasLoading = False
			if Game.currentPiece:
				Game.userInput()
				Game.gravity()
				Game.removeRows()
			elif(Game.obstacleGroup.getMaxRow()):
				print('GAME OVER!')
				print('Final Score: ', Game.score)
				break
			else:
				Game.spawnBlock()
				Display.renderNextPiece()
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
