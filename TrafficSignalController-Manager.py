
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import random
from threading import Condition, Lock, Thread
import time

class Light(Enum):
    RED = 1
    YELLOW = 2
    GREEN = 3

class Signal(Enum):
    NORTH_SOUTH = 1
    EAST_WEST = 2
    
class Directions(Enum):
    NORTH = 1
    SOUTH = 2
    EAST = 3
    WEST = 4
    

class Car(Thread):
    def __init__(self, direction: Directions, controller: TrafficController):
        super().__init__()
        self.direction = direction
        self.controller = controller

    def run(self):
        signal_group = self.controller.directions_to_signal[self.direction]
        with self.controller.signal_groups[signal_group]:
            while self.controller.lights[self.direction] != Light.GREEN:
                self.controller.signal_groups[signal_group].wait()

            print(f"Signal turned GREEN for {self.direction}. Car going...")
            time.sleep(1)

class TrafficController:
    def __init__(self):
        self.lights = {
            Directions.NORTH: Light.RED, \
            Directions.SOUTH: Light.RED, \
            Directions.EAST: Light.RED, \
            Directions.WEST: Light.RED \
        }

        self.directions_to_signal = {
            Directions.NORTH: Signal.NORTH_SOUTH,
            Directions.SOUTH: Signal.NORTH_SOUTH,
            Directions.EAST: Signal.EAST_WEST,
            Directions.WEST: Signal.EAST_WEST
        }

        self.signal_to_directions = {
            Signal.NORTH_SOUTH: [Directions.NORTH, Directions.SOUTH],
            Signal.EAST_WEST: [Directions.EAST, Directions.WEST]
        }
        
        self.lock = Lock()
        ns_condition = Condition(self.lock)
        ew_condition = Condition(self.lock)
        self.signal_groups = {Signal.NORTH_SOUTH: ns_condition, Signal.EAST_WEST: ew_condition}


    def start(self):
        while True: 
            for signal, condition in self.signal_groups.items():
                with condition:
                    directions = self.signal_to_directions[signal]
                    for d in directions:
                        self.lights[d] = Light.GREEN
                        condition.notify_all()
                
                print(f"Signal for {signal} turned GREEN")
                time.sleep(2)

                with condition:
                    directions = self.signal_to_directions[signal]
                    for d in directions:
                        self.lights[d] = Light.YELLOW
                        # condition.notify_all()
                
                print(f"Signal for {signal} turned YELLOW")
                time.sleep(2)

                with condition:
                    directions = self.signal_to_directions[signal]
                    for d in directions:
                        self.lights[d] = Light.RED
                        # condition.notify_all()
                
                print(f"Signal for {signal} turned RED")
                time.sleep(2)
            print("New loop")


if __name__ == "__main__":
    tc = TrafficController()

    def create_car(tc):
        direction = random.sample(k=1, population=[Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST])[0]
        car = Car(direction, tc)
        car.start()
        return car

    futures = []
    with ThreadPoolExecutor(20) as executor:
        for _ in range(10):
            futures.append(executor.submit(create_car, tc))

    tc.start()

        