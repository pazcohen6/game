

class Impossible(Exception):
    """Exception raised when an action is impossible to be performed.

    The reason is given as the exception message.
    """

class QuitWithoutSaveing(SystemExit):
    """Can be raised to exit the game without automatically saving."""