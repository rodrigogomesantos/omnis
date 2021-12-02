from ..new_serial.movment import showMoves
import externallibs.new_serial.movment as move
import timeit

class loop():
    def __init__(self, _loop_type, **kwargs) -> None:
        self.type = _loop_type
        self.kwargs = kwargs
        self.break_function = self.kwargs.get("break_function")
        self.range = kwargs.get("range")
        self.start = getattr(self, f"_{self.type}")
        self.counter = 0
        self.outPut_function = 0 

    def _while(self, function, *ags, **kws):
        self.counter = 0
        while not self.break_function():
            self.outPut_function = function(*ags, **kws)
            self.counter+=1
        return self.counter, self.outPut_function

    def _for(self, function, *args, **kwargs):
        self.counter = 0
        for _c_ in self.range:
            self.outPut_function = function(*args, **kwargs)
            self.counter = _c_
        return self.counter, self.outPut_function

    def break_verify(self):
        self.break_function()

class Process():
    def __init__(self, loop, *args, **kwargs) -> None:
        self.loop = loop
        self.ars = args
        self.kgs= kwargs

    def start(self):
        self.loop.start(*self.ars, **self.kgs)

    def inform():
        loop.inform()

    def before_start(self, positon, moveFunc):
        move.setPositon(positon, moveFunc)
