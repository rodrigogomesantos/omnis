
class serialException(Exception):
    def __str__(self) -> str:
        return "serialException >> "

class serialclosed(serialException):
    def __str__(self) -> str:
        return super().__str__() + "serial connection couldn't be established."

class serialnotrespond(serialException):
    def __str__(self) -> str:
        return super().__str__() + "serial connection stopped responding."

