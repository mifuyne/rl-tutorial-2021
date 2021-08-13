# game/exceptions.py

class Impossible(Exception):
    """Exception raised when the impossible is performed.
    
    Reason provided as the exception message.
    """


class QuitWithoutSaving(SystemExit):
    """Can be raised to exit the game without automatically saving."""
