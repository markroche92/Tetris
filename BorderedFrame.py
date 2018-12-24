from tkinter import *


class BorderedFrame:

	def __init__(self, parentFrame, borderWidth, totalWidth, totalHeight,
	             createMainAreaFunction, borderColour, gridWidth = None):

		# Class allows for the border to not have same width as inner grid
		if not gridWidth: gridWidth = borderWidth

		self.minRow = 0
		self.minCol = 0
		self.maxRow = int(max(0, totalHeight / gridWidth - 1))
		self.maxCol = int(max(0, totalWidth / gridWidth - 1))

		# Window Border Creation
		windowBorderNorth = Frame(parentFrame, height = borderWidth,
		                          width = totalWidth - borderWidth, bg = borderColour)
		windowBorderWest = Frame(parentFrame, height = totalHeight - borderWidth,
		                         width = borderWidth, bg = borderColour)
		self.windowBorderSouth = Frame(parentFrame, height = borderWidth,
		                          width = totalWidth - borderWidth, bg = borderColour)
		self.windowBorderEast = Frame(parentFrame, height = totalHeight - borderWidth,
		                         width = borderWidth, bg = borderColour)

	 	# Window Border Placement
		windowBorderNorth.grid(row = self.minRow, column = self.minCol,
		                       columnspan = self.maxCol, sticky = 'N')
		windowBorderWest.grid(row = self.minRow + 1, column = self.minCol, rowspan = self.maxRow, sticky = 'W')

		createMainAreaFunction()

		self.addBorderSouthEast()

	def addBorderSouthEast(self):

		# Window Borders South and East
		self.windowBorderSouth.grid(column = self.minCol + 1, row = self.maxRow,
		                       columnspan = self.maxCol, sticky = 'S')
		self.windowBorderEast.grid(row = self.minRow, column = self.maxCol,
		                      rowspan = self.maxRow, sticky = 'E')
