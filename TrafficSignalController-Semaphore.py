from enum import Enum
from threading import BoundedSemaphore, Condition, Lock, Thread
import time

class Lights(Enum):
    GREEN = 4
    YELLOW = 3
    RED = 5

class TrafficSensor(Thread):
    def __init__(self, name, semaphore):
        super().__init__(name=name)
        self.semaphore = semaphore

    def run(self):
        while True: 
            with self.semaphore:
                print(f"{self.name}: Acquired semaphore.")
                time.sleep(2)
                print(f"{self.name}: Done with signal")

            # Tiny wait to allow other thread to acquire semaphore
            time.sleep(1)
            
class TrafficController:
    def __init__(self):
        self.semaphore = BoundedSemaphore(1)
        self.north_south = TrafficSensor(name="North-South", semaphore=self.semaphore)
        self.east_west = TrafficSensor(name="East-West", semaphore=self.semaphore)

        self.north_south.start()
        self.east_west.start()

if __name__ == "__main__":
    tc = TrafficController()





