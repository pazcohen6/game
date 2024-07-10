# Define a base class for all actions
class Action:
    pass

# Define a subclass for escape action.
#TODO
class EscapeAction(Action):
    pass

# Define a subclass for movement action, with includes info about movement direction
class MovementAction(Action):
    # Constracter for MovementAction
    # dx : movement in x direction
    # dx : movement in y direction
    def __init__ (self,dx : int,dy : int):
        super().__init__()

        self.dx = dx
        self.dy = dy
