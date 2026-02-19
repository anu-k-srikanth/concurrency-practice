
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from threading import Condition, Event, Lock, Thread
import time

MAX_CAPACITY = 5
queue = deque()
lock = Lock()
can_write = Condition(lock)
can_read = Condition(lock)

PRODUCER_THREADS = 4
CONSUMER_THREADS = 5

stop_threads = Event()


def producer(item):
    while not stop_threads.is_set():
        with can_write:
            print(f"Producer acquired lock")
            print(f"queue {queue}")
            while len(queue) == MAX_CAPACITY:
                print(f"Producer wating queue to clear up")
                can_write.wait()
            queue.append(item)
            print(f"Producer added {item}")
            can_read.notify_all()
        time.sleep(1)

def consumer():
    while True:
        with can_read:
            print(f"Consumer acquired lock")
            print(f"queue {queue}")
            while len(queue) == 0:
                if stop_threads.is_set():
                    print(f"stop_threads is set. Exiting")
                    return
                print(f"Consumer wating for items to be added to queue")
                can_read.wait()
            
            item = queue.popleft()
            print(f"Consumer received {item}")
            can_write.notify_all()
        time.sleep(2)



if __name__ == "__main__":

    producer_threads = [Thread(target=producer, args=(i,)) for i in range(PRODUCER_THREADS)]
    consumer_threads = [Thread(target=consumer) for i in range(CONSUMER_THREADS)]

    for p in producer_threads:
        p.start()

    for c in consumer_threads:
        c.start()

    time.sleep(5)
    stop_threads.set()

    with can_read:
        can_read.notify_all()
    time.sleep(5)
    with can_write:
        can_write.notify_all()

    for t in producer_threads + consumer_threads:
        t.join()
