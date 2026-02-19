


from threading import Condition, Lock
import threading
import time


class CountdownLatch:
    def __init__(self, count: int):
        self.counter = count
        self._lock = Lock()
        self._condition = Condition(self._lock)

    def count_up(self) -> None:
        with self._condition:
            self.counter += 1

    def count_down(self) -> None:
        with self._condition:
            self.counter -= 1
            if self.counter == 0:
                self._condition.notify_all()

    def wait(self) -> None:
        """
        Stop the current thread here until the count is zero.
        If the count is already zero, do not stop.
        """
        with self._condition:
            while self.counter != 0:
                self._condition.wait()
if __name__ == "__main__":
    def worker(latch: CountdownLatch, worker_id: int):
        """Act like a worker doing a job."""
        print(f"Worker {worker_id} starting...")
        time.sleep(0.5)  # Pretend to work
        print(f"Worker {worker_id} done!")
        latch.count_down()

    # Create latch with count = 3 (we expect 3 workers)
    latch = CountdownLatch(3)

    # Start 3 worker threads
    for i in range(3):
        t = threading.Thread(target=worker, args=(latch, i))
        t.start()

    # Main thread pauses here until workers finish
    print("Main thread waiting for workers...")
    latch.wait()
    print("All workers completed!")