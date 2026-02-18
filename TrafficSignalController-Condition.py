from enum import Enum
from threading import BoundedSemaphore, Condition, Lock, Thread
import time

class Status(Enum):
    WAIT = 1
    READY = 2

class TrafficSensor(Thread):
    def __init__(self, condition, other_direction_condition, i, status):
        super().__init__()
        self.condition = condition
        self.other_direction_condition = other_direction_condition
        self.i = i
        self.status = status

    def run(self):
        while True:
            with self.condition:
                while self.status[self.i] == Status.WAIT:
                    self.condition.wait()

                print(f"Light {self.i} is now GREEN for 4 seconds")
                time.sleep(1)
                print(f"Light {self.i} is now YELLOW for 3 seconds")
                time.sleep(1)
                print(f"Light {self.i} is now RED until other light is over")
                self.status[self.i] = Status.WAIT

            with self.other_direction_condition:
                self.status[(self.i+1)%len(self.status)] = Status.READY
                self.other_direction_condition.notify_all()
    

class TrafficController:
    def __init__(self):
        self.lock = Lock()
        self.north_south_condition = Condition(self.lock)
        self.east_west_condition = Condition(self.lock)
        self.status = [Status.READY, Status.WAIT]

        self.north_south = TrafficSensor(self.north_south_condition, self.east_west_condition, 0, self.status)
        self.east_west = TrafficSensor(self.east_west_condition, self.north_south_condition, 1, self.status)

        self.north_south.start()
        self.east_west.start()

if __name__ == "__main__":
    tc = TrafficController()

    



