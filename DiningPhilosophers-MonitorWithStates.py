

from enum import Enum
import random
from threading import Condition, Lock, Thread
import time

N = 5

class State(Enum):
    THINKING = 0
    HUNGRY = 1
    EATING = 2


class Monitor():
    def __init__(self):
        # This lock locks the state updates and makes them atomic
        self._lock = Lock()
        self._philosopher_states = [State.THINKING for _ in range(N)]
        self.conditions = [Condition(self._lock) for _ in range(N)]

    def left_neighbor(self, i):
        return i-1 if i > 0 else N-1
    
    def right_neighbor(self, i):
        return (i + 1) % N
    
    def _try_to_eat(self, i):
        if self._philosopher_states[i] == State.HUNGRY and \
            self._philosopher_states[self.left_neighbor(i)] != State.EATING and \
                self._philosopher_states[self.right_neighbor(i)] != State.EATING:
            
            self._philosopher_states[i] = State.EATING
            self.conditions[i].notify()
    
    def pickup_forks(self, i):
        with self._lock:
            self._philosopher_states[i] = State.HUNGRY
            while True: 
                self._try_to_eat(i)
                if self._philosopher_states[i] == State.EATING:
                    break
                self.conditions[i].wait(timeout=0.5)

    def put_down(self, i):
        with self._lock:
            self._philosopher_states[i] = State.THINKING
            self._try_to_eat(self.left_neighbor(i))
            self._try_to_eat(self.right_neighbor(i))

class Philosopher(Thread):
    def __init__(self, i, monitor: Monitor):
        super().__init__(name=str(i))
        self.i = i
        self.monitor = monitor

    def think(self):
        print(f"Philosopher {self.name} is thinking", flush=True)
        time.sleep(random.randint(0,4))

    def eat(self):
        print(f"Philosopher {self.name} is eating", flush=True)
        time.sleep(random.randint(0,4))
    
    def run(self):
        while True:
            self.think()
            self.monitor.pickup_forks(self.i)
            self.eat()
            self.monitor.put_down(self.i)

if __name__ == "__main__":
    threads = []
    monitor = Monitor()
    for i in range(N):
        t = Philosopher(i, monitor)
        t.start()
        threads.append(t)

    for t in threads: 
        t.join()

    
    # def _get_neighbor_states(self, i):
    #     left_neighbor = i-1 if i > 0 else N-1
    #     right_neighbor = (i+1) % N

    #     return self._philosopher_states[left_neighbor], self._philosopher_states[right_neighbor]


    # def set_state(self, i, state):
    #     with self._lock:
    #         if state == State.HUNGRY:
    #             self.try_to_eat(i)
    #         elif state == State.THINKING:
    #             self._philosopher_states[i] = state
    #             left_neighbor = i-1 if i > 0 else N-1
    #             right_neighbor = (i+1) % N

    #             self.try_to_eat(left_neighbor)
    #             self.try_to_eat(right_neighbor)


    # def try_to_eat(self, i):
    #     left, right = self._get_neighbor_states(i)
    #     if left != State.EATING and right != State.EATING:
    #         self._philosopher_states[i] = State.EATING
