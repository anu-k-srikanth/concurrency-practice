

import random
from threading import Lock, Thread
import time

N = 5
forks = [True for i in range(N)]
# [1,2,3,4,5]
# [P1, P2, P3, P4, P5]

MAX_WAIT_TIME = 5


class Waiter():
    def __init__(self):
        self._lock = Lock()

    def acquire_forks(self, i):
        with self._lock:
            left, right = i, (i+1)%N
            if forks[left] and forks[right]:
                forks[left] = False
                forks[right] = False
                return True
            else: 
                return False
            
    def release_forks(self, i):
        with self._lock:
            left, right = i, (i+1)%N
            forks[left] = True
            forks[right] = True

class Philosopher(Thread):
    def __init__(self, i, waiter: Waiter):
        super().__init__(name=str(i))
        self.i = i
        self.waiter = waiter
        self.waiting_since = None

    def think(self):
        print(f"Philosopher {self.name} is thinking", flush=True)
        time.sleep(random.randint(0,4))

    def eat(self):
        self.waiting_since = time.time()
        while not self.waiter.acquire_forks(self.i):
            print(f"Philosopher {self.name} could not acquire forks. Waiting...", flush=True)
            if time.time() - self.waiting_since > MAX_WAIT_TIME: 
                print(f"Philosopher {self.name} is STARVING")
            time.sleep(1)

        print(f"Philosopher {self.name} is eating", flush=True)
        time.sleep(1)
        self.last_chosen = time.time()
        self.waiter.release_forks(self.i)
    
    def run(self):
        while True:
            self.think()
            self.eat()


if __name__ == "__main__":
    threads = []
    waiter = Waiter()
    for i in range(N):
        t = Philosopher(i, waiter)
        t.start()
        threads.append(t)

    for t in threads: 
        t.join()
    
