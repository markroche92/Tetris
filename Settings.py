
class Settings:

    DIFFICULTY_EASY = 1
    DIFFICULTY_INT = 2
    DIFFICULTY_HARD = 3

    difficulties = [DIFFICULTY_EASY,
                    DIFFICULTY_INT,
                    DIFFICULTY_HARD]

    difficultiesString = ['Easy',
                    'Intermediate',
                    'Hard']

    def __init__(self):
        self.difficulty = self.DIFFICULTY_EASY

    def setDifficult(self, value):
        self.difficulty = value
