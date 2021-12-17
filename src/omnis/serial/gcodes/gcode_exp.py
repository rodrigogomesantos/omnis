class gcodeException(Exception):
    def __str__(self) -> str:
        return "gcodeException >> "

class M114unpackFail(gcodeException):
    def __str__(self, who, message) -> str:
        return super().__str__() + f"{who} can't unpack {message}"