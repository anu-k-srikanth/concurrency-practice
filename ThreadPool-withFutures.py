from __future__ import annotations
from collections import deque
import random
from threading import Condition, Lock, Thread
import time
import typing as T

# You submit a task.

# ThreadPool:
# Creates a Future
# Puts (task, future) in queue

# Worker thread:
# Takes task from queue
# Executes it
# Calls future.set_result(value)
# Any thread waiting on future.result() wakes up.
# They all receive the same result.


# This class is a promise of future results. 
class Future:
    def __init__(self):
        self.done = False
        self._result = None
        self._exception = None
        self._lock = Lock()
        self._condition = Condition(self._lock)
    
    # This function sets the result when it becomes available and notifies any threads waiting for this 
    # Other threads could be blocked on `get_result()` when the condition is blocked so now that the result
    # is available, we can notify
    def set_result(self, result):
        with self._condition:
            self._result = result
            self.done = True
            self._condition.notify_all()
    
    # Same as result for this one except it's if an exception was thrown. The caller may choose to rethrow exception
    def set_exception(self, exception):
        with self._condition:
            self._exception = exception
            self.done = True
            self._condition.notify_all()

    # Check whether result is available.
    def get_result(self, timeout=None):
        with self._condition:
            while not self.done:
                # We don't need timeout here because after result is written to the future, 
                # we notify all on this condition so we will leave this loop. 
                self._condition.wait(timeout=timeout)
            if self._exception:
                raise self._exception
            return self._result

class ThreadPoolThread(Thread):
    def __init__(self, name: str, thread_pool: ThreadPool):
        super().__init__(name=name)
        self.thread_pool = thread_pool
        
        self.start()

    def run(self):
        while True: 
            task, args, kwargs, future = self.thread_pool._get_task_from_queue()
            if task is None: 
                print(f"Thread {self.name} received SENTINEL and is shutting down")
                break
            task(*args, kwargs)

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
            task, args, kwargs, future = self.queue.popleft()
            return task, args, kwargs, future

    def submit_task(self, task, args, kwargs=None):
        future = Future()
        def wrapped_task(*args, **kwargs):
            try:
                result = task(*args, **(kwargs or {}))
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)

        with self.can_read:
            self.queue.append((wrapped_task, args, kwargs, future))
            self.can_read.notify()
        return future

    def shutdown(self):
        with self.can_read:
            for _ in range(len(self.threads)):
                self.queue.append((None, None, None, None))
                # Any time you're writing to the queue, notify the waiting reader threads.
                self.can_read.notify()
        
def dummy_function(args, kwargs=None) -> int:
    print(f"Function executed with {args}")
    time.sleep(4)
    return random.randint(1,9)

if __name__ == "__main__":
    tp = ThreadPool(3)

    futures: T.List[Future] = []
    for i in range(10):
        fut = tp.submit_task(dummy_function, (i,))
        futures.append(fut)

    for f in futures: 
        print(f"Got result: {f.get_result()} and exception {f._exception}")

    tp.shutdown()


