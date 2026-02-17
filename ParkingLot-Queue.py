
from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor
import random
from threading import BoundedSemaphore, Condition, Lock, RLock, Thread
import time
import typing as T

class LotFullError(Exception):
    pass

class CarNotFound(Exception):
    pass

class QueueFullError(Exception):
    pass

class ParkingSection:
    def __init__(self, id, capacity, condition: Condition):
        self.id = id
        self.capacity = capacity
        self.cars = set()
        self._lock = RLock() # This lock locks the cars set 
        self._can_permit = condition # This condition is a global condition that determines whether there are spots available

    def enter(self, car):
        with self._lock:
            if len(self.cars) < self.capacity:
                self.cars.add(car)
            else: 
                print(f"Section {self.id} parking lot full")
                raise LotFullError()

    def exit(self, car):
        with self._lock:
            if car in self.cars:
                self.cars.remove(car)
            else: 
                print(f"Section {self.id} car {car} not found")
                raise CarNotFound()
            
        # Notify after releasing the section lock. It not necessary to hold the section lock while notifying and
        # doing so could introduce some deadlock scenarios. 
        # We may have ordering issues that result in deadlock behavior
        with self._can_permit:
            self._can_permit.notify()

    def is_at_capacity(self):
        with self._lock: 
            return len(self.cars) == self.capacity
        
    def print(self):
        print(f"Section {self.id} with cars {self.cars}", flush=True)

class ParkingLot:
    def __init__(self, num_sections, capacity):
        self._queue_lock = Lock()
        self.queue = deque()
        self.queue_capacity = capacity

        self._can_permit_car = Condition(self._queue_lock)
        self.queue_manager = Thread(target=self._run_queue_manager, daemon=True)
        # Fixed thread to use `.start()` instead of `.run()`. run method blocks the main thread.
        self.queue_manager.start()

        self.parking_sections = {}
        for i in range(num_sections):
            self.parking_sections[i] = ParkingSection(i, capacity, self._can_permit_car)

    def _run_queue_manager(self):
        while True:
            self._permit_queued_car()

    def _permit_queued_car(self):
        with self._can_permit_car:
            while not self.queue or self._any_section_available():
                self._can_permit_car.wait()

            check_car = self.queue[0]
            section = self._park_in_available_section(check_car)
            if section: 
                car = self.queue.popleft()
            else: 
                # Why wait here? 
                self._can_permit_car.wait()
                # raise RuntimeError(f"Tried to permit queued car {check_car} into section {section.id if section else None} ")

    # def _add_car_to_queue(self, car):    
    #     with self._queue_lock:
    #         if len(self.queue) < self.queue_capacity:
    #             self.queue.append(car)
    #         else: 
    #             raise RuntimeError()

    def _get_assigned_parking_section(self, car) -> T.Tuple[int, ParkingSection]:
        assignment = hash(car) % len(self.parking_sections)
        return assignment, self.parking_sections[assignment]
    
    def _find_car(self, car):
        for section in self.parking_sections.values():
            with section._lock:
                if car in section.cars: 
                    return section
        raise ValueError("Car {car} not present in parking lot")

    # def _get_parking_section(self, car):
    #     assignment, section = self._get_assigned_parking_section(car)
    #     i = assignment
    #     for _ in range(len(self.parking_sections)):
    #         section: ParkingSection = self.parking_sections[i]
    #         if not section.is_at_capacity():
    #             return section
    #         i = (i+1) % len(self.parking_sections)
    #     return None
    
    def _any_section_available(self):
        for section in self.parking_sections.values():
            with section._lock:
                if len(section.cars) < section.capacity:
                    return True
        return False

    def _park_in_available_section(self, car):
        for section in self.parking_sections.values(): 
            with section._lock:
                if not section.is_at_capacity():
                    section.enter(car)
                    return section
        print(f"All sections full. Car {car} cannot be parked")
        return None

    def enter(self, car):
        section = self._park_in_available_section(car)
        if section is None: 
            with self._can_permit_car:
                # We do not need additional function that holds the lock because we're inside the condition
                # self._add_car_to_queue(car)
                if len(self.queue) < self.queue_capacity:
                    self.queue.append(car)
                    self._can_permit_car.notify()
                else: 
                    print(f"Reached queue max capacity: {self.queue}")
        self.print_state()

    def exit(self, car):
        section = self._find_car(car)
        section.exit(car)
        self.print_state()

    def print_state(self):
        for section in self.parking_sections.values():
            section.print()
        print(f"Queue: {self.queue}", flush=True)
 
if __name__ == "__main__":
    pl = ParkingLot(num_sections=3, capacity=2)

    def car_enter(i):
        pl.enter(i)
        # pl.print_state()
        time.sleep(random.randint(1,3))

    def car_exit(i):
        pl.exit(i)
        pl.print_state()
        time.sleep(random.randint(1,3))

    with ThreadPoolExecutor(20) as executor:
        for i in range(20):
            executor.submit(car_enter, i)
            if i % 2 == 0 and random.randint(0,1): 
                executor.submit(car_exit, i)

    print(executor._work_queue.qsize)