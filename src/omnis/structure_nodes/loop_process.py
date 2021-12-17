class process():
    def __init__(self, loop, *args, **kwargs) -> None:
        self.loop = loop
        self.ars = args
        self.kgs= kwargs

    def start(self):
        self.loop.start(*self.ars, **self.kgs)