from __future__ import annotations
from collections import deque
import random
import sys
from threading import Condition, Lock, Thread
import threading
import time
import traceback
import typing as T

import faulthandler, signal
faulthandler.enable()


def dump_threads():
    print("\n=== THREAD DUMP ===\n")
    for thread in threading.enumerate():
        print(f"Thread Name: {thread.name}")
        print(f"Thread ID: {thread.ident}")
        print(f"Alive: {thread.is_alive()}")
        print("-" * 40)

        frame = sys._current_frames().get(thread.ident)
        if frame:
            traceback.print_stack(frame)
        print("\n")


class Producer(Thread):
    def __init__(self, name, producer_queue: BoundedQueue, consumer_queue: BoundedQueue):
        super().__init__(name=name)
        self.producer_queue = producer_queue
        self.consumer_queue = consumer_queue

    def run(self):
        while True:
            item = self.producer_queue.get()

            if item is None: 
                print(f"Producer thread {self.name} received SENTINEL value. Shutting down")
                break

            print(f"Producer thread {self.name} picked up item {item}")
            self.consumer_queue.put(item)
            print(f"Producer thread {self.name} put item {item} in consumer queue")

            time.sleep(random.randint(0,4))
            


class Consumer(Thread):
    def __init__(self, name, consumer_queue: BoundedQueue):
        super().__init__(name=name)
        self.consumer_queue = consumer_queue

    def run(self):
        while True: 
            # We do not want to check whether there is an item in the queue because between that check and retrieving the item, 
            # another thread couldve gotten it 
            item = self.consumer_queue.get()

            if item is None: 
                print(f"Consumer thread {self.name} received SENTINEL value. Shutting down")
                break

            print(f"Consumer thread {self.name} picked up item {item}")

            time.sleep(random.randint(0,4))
            # faulthandler.dump_traceback()


class BoundedQueue:
    def __init__(self, capacity):
        self.queue = deque()
        self._capacity = capacity
        self._lock = Lock()
        self._can_read = Condition(self._lock)
        self._can_write = Condition(self._lock)
        self._closed = False

    def shutdown(self):
        with self._lock:
            self._closed = True
            self._can_read.notify_all()
            self._can_write.notify_all()

    def put(self, item: int | None):
        with self._can_write:
            if self._closed: 
                raise RuntimeError("Cannot add item to a closed queue")
            while len(self.queue) >= self._capacity:
                self._can_write.wait()
            self.queue.append(item)
            self._can_read.notify()
    
    def size(self):
        # Do not want to do `with self._can_write and self._can_read:` because it does not acquire both conditions. 
        with self._lock:
            return len(self.queue)
    
    def get(self):
        with self._can_read:
            while len(self.queue) == 0:
                if self._closed:
                    return None
                self._can_read.wait()
            item = self.queue.popleft()
            self._can_write.notify()
            return item
        
    
if __name__ == "__main__":
    # faulthandler.dump_traceback_later(10, repeat=True)

    producer_bq = BoundedQueue(capacity=2)
    consumer_bq = BoundedQueue(capacity=3)

    num_producer_threads = 5
    num_consumer_threads = 3

    producer_threads = []
    for i in range(num_producer_threads):
        t = Producer(f"ProducerThread-{i}", producer_bq, consumer_bq)
        t.start()
        producer_threads.append(t)

    consumer_threads = []
    for i in range(num_consumer_threads):
        t = Consumer(f"ConsumerThread-{i}", consumer_bq)
        t.start()
        consumer_threads.append(t)
    
    for i in range(10):
        producer_bq.put(i)

    producer_bq.shutdown()

    for t in producer_threads:
        t.join()
        
    consumer_bq.shutdown()
        
    for t in consumer_threads:
        t.join()

    dump_threads()
    
    

 