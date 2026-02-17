from __future__ import annotations
from collections import deque
from threading import Condition, Lock, Thread


class ThreadPoolThread(Thread):
    def __init__(self, name: str, thread_pool: ThreadPool):
        super().__init__(name=name)
        self.thread_pool = thread_pool
        
        self.start()

    def run(self):
        while True: 
            task, args, kwargs = self.thread_pool._get_task_from_queue()
            if task is None: 
                print(f"Thread {self.name} received SENTINEL and is shutting down")
                break
            task(*args, **(kwargs or {}))

class ThreadPool:
    def __init__(self, num_threads):
        self.threads = []
        self.queue = deque()
        self.lock = Lock()
        self.can_read = Condition(self.lock)

        for i in range(num_threads):
            self.threads.append(ThreadPoolThread(name=f"Thread-{i}", thread_pool=self))
    
    def _get_task_from_queue(self): 
        with self.can_read:
            while len(self.queue) == 0: 
                self.can_read.wait()
            task, args, kwargs = self.queue.popleft()
            return task, args, kwargs

    def submit_task(self, task, args, kwargs=None):
        with self.can_read:
            self.queue.append((task, args, kwargs))
            self.can_read.notify()

    def shutdown(self):
        with self.can_read:
            for _ in range(len(self.threads)):
                self.queue.append((None, None, None))
                # Any time you're writing to the queue, notify the waiting reader threads.
                self.can_read.notify()
        
def dummy_function(args, kwargs=None):
    print(f"Function executed with {args}")

if __name__ == "__main__":
    tp = ThreadPool(3)

    for i in range(10):
        tp.submit_task(dummy_function, (i,))

    tp.shutdown()


