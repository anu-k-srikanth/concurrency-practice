

import random
from threading import Lock, Thread
import time

N = 3
forks = [Lock() for i in range(N)]
counter_lock = Lock()
counter = [0, 0, 0]
# [1,2,3,4,5]
# [P1, P2, P3, P4, P5]

class Philosopher(Thread):
    def __init__(self, i):
        super().__init__(name=str(i))
        self.i = i

    def think(self):
        print(f"Philosopher {self.name} is thinking", flush=True)
        # time.sleep(random.randint(0,4))

    def eat(self):
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
                with counter_lock:
                    counter[i] += 1
                # time.sleep(1)
    
    def run(self):
        stop_thread = False
        while True:
            with counter_lock: 
                for count in counter: 
                    if count > 20: stop_thread = True
            if stop_thread: break
            self.think()
            self.eat()


if __name__ == "__main__":
    threads = []
    for i in range(3):
        t = Philosopher(i)
        t.start()
        threads.append(t)

    for t in threads: 
        t.join()

    print(counter)
    
