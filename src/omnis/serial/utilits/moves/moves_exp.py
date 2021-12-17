class movesException(Exception):
    def __str__(self) -> str:
        return "movesException >> "

class axisundefined(movesException):
    def __str__(self, axis, id, _dict) -> str:
        return super().__str__() + f"axis {axis} is 'variable' in {id}, but has undefined value in {_dict}."