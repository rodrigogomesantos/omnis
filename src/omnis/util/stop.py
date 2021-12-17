import threading


class reason():
    def __init__(self, name, logger, initial_value = False) -> None:
        self.logger = logger
        self.name=name
        self.initial_value = initial_value
        self.stopped = threading.Event()
        self.stopped.set() if initial_value is True else self.stopped.clear()
        self.lockS = threading.Lock()
        self.lockR = threading.Lock()

    def stop(self):
        self.lockS.acquire()
        self.stopped.set()
        self.logger.info(f"{self.name} requested a stop")
        print(f"{self.name} requested a stop")
        self.lockS.release()
    def reset(self):
        self.lockR.acquire()
        self.stopped.clear()
        self.logger.info(f"{self.name} returned to initial value")
        print(f"{self.name} returned to initial value")
        self.lockR.release()

    def isStopped(self):
        return self.stopped.is_set()
