
from concurrent.futures import Future, ThreadPoolExecutor
import random
from threading import BoundedSemaphore, Lock, RLock
import time
import typing as T

class ParkingLot:
    def __init__(self, capacity):
        self.cars = set()
        self._lock = RLock()
        self._semaphore = BoundedSemaphore(capacity)

    def enter(self, car):
        with self._lock:
            print(f"Car {car} attempting to enter parking lot")
            acquired = self._semaphore.acquire(timeout=1)
            if acquired:
                self.cars.add(car)
            else: 
                print(f"Car {car} could not enter parking lot")
                return
        return f"Car {car} entered"

    def exit(self, car):
        with self._lock:
            if car in self.cars:
                print(f"Car {car} attempting to exit parking lot")
                self.cars.remove(car)
            else: 
                raise ValueError(f"Car {car} not in parking lot")
        self._semaphore.release()
        return f"Car {car} exited"


if __name__ == "__main__":
    pl = ParkingLot(3)
    # for car in range(7):
    #     pl.enter(car)

    def enter_and_wait(pl, car):
        resp = pl.enter(car)
        time.sleep(random.randint(1,4))
        return resp

    def random_exit(pl: ParkingLot, car):
        resp = pl.exit(car)
        time.sleep(random.randint(1,4))
        return resp

    futures: T.List[Future] = []
    with ThreadPoolExecutor() as executor:
        for car in range(7):
            enter = executor.submit(enter_and_wait, pl, car)
            if car % 2 == 0:
                exit = executor.submit(random_exit, pl, car)
                futures.append(exit)
            futures.append(enter)


    for r in futures: 
        try: 
            print(f"Result is {r.result()}")
        except Exception as e: 
            print(f"Exception {e}")
    
    print(pl.cars)
    
