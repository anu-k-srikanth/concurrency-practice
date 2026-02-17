

import random
from threading import Lock, Semaphore, Thread
import time


N = 2
forks = [Lock() for i in range(N)]
semaphore = Semaphore(N-1)

class Philosopher(Thread):
    def __init__(self, i):
        super().__init__(name=str(i))
        self.i = i

    def think(self):
        print(f"Philosopher {self.name} is thinking", flush=True)
        time.sleep(random.randint(0,4))

    def eat(self):
        with semaphore: 
            # We impose a global order on the forks
            left_fork = self.i
            right_fork = (self.i+1)%N

            first = min(left_fork, right_fork)
            second = max(left_fork, right_fork)

            with forks[first]:
                print(f"Philosopher {self.name} picked up fork {first}", flush=True)
                with forks[second]:
                    print(f"Philosopher {self.name} picked up fork {second}", flush=True)
                    print(f"Philosopher {self.name} is eating", flush=True)
                    time.sleep(1)
    
    def run(self):
        while True:
            self.think()
            self.eat()


if __name__ == "__main__":
    threads = []
    for i in range(N):
        t = Philosopher(i)
        t.start()
        threads.append(t)

    for t in threads: 
        t.join()
    
