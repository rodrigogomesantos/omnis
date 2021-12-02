class reason():
    def __init__(self, name, logger, initial_value = False) -> None:
        self.logger = logger
        self.name=name
        self.initial_value = initial_value
        self.stopped = self.initial_value

    def stop(self):
        self.logger.info(f"{self.name} requested a stop")
        self.stopped = not self.initial_value
    
    def reset(self):
        self.logger.info(f"{self.name} returned to initial value")
        self.stopped = self.initial_value

    def isStopped(self):
        return self.stopped
