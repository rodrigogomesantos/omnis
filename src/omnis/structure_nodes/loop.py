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
        while not self.break_function():
            self.counter = 0
            while not self.pause_function():
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