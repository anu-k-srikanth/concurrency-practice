

from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor
import random
from threading import Condition, Lock, RLock, Thread
import time
from typing import List

# Follow ups: 
# What happens if we have 10K URLs? 
# Our memory grows unbounded and we would need to place limits. 
# We can add a capacity limit for our queue and add a condition so that writers will be queued 
# and will need to wait before adding more. Writer threads will be paused while the consumers catch up. 
# We would need to break up this logic and then this turns into a producer-consumer problem.

# Space constraints: 
# We may want to keep the dedupe set in an external storage that is very quick: 
# 1. Redis cache - key-value store that is very fast.
# 2. Bloom filters - 
#       probabalistic data structure where an item that is being stored is hashed using a variety 
#       of different methods. This means that it can tell us with a 100% certainty if an item is 
#       not in the cache. - If it says item is in cache - there may be a false positive. 
#       but it will never return an item is not in cache when it is.


class HtmlParser:
    def getUrls(self, url):
        time.sleep(1)
        urls = []
        for _ in range(random.randint(1,5)):
            urls.append(f"url-{random.randint(1,10)}")
        return urls


class WebCrawler:
    def __init__(self):
        self.queue = deque()
        self.lock = RLock()
        self.can_read = Condition(self.lock)
        self.htmlParser = HtmlParser()
        self.dedupe = set()
        self.crawled_urls = []
        self.active_workers = 0

    def write_to_queue(self, urls):
        with self.lock:
            for url in urls: 
                if url not in self.dedupe:
                    self.crawled_urls.append(url)
                    self.queue.append(url)
                    self.dedupe.add(url)
                    self.can_read.notify()

    def process_url(self):
        while True: 
            with self.can_read:
                is_done = False
                while len(self.queue) == 0:
                    if self.active_workers == 0: 
                        is_done = True
                        break
                    self.can_read.wait()
                
                if is_done: 
                    print(f"No more active workers. Exiting")
                    break

                self.active_workers += 1
                url = self.queue.popleft()
                # if url is SENTINEL: 
                #     print(f"Received SENTINEL value {SENTINEL}. Shutting down thread...", flush=True)
                #     break 

            print(f"URL {url} retrieved from queue", flush=True)
            new_urls = self.htmlParser.getUrls(url)
            print(f"Retreived {new_urls} from HTML parser", flush=True)

            with self.can_read:
                self.write_to_queue(new_urls)
                self.active_workers -= 1
                self.can_read.notify_all()
        

    def start(self, start_url):
        num_threads = 3
        futures: List[Future] = []
        self.write_to_queue([start_url])
        with ThreadPoolExecutor(num_threads) as executor:
            for _ in range(num_threads):
                f = executor.submit(self.process_url)
                futures.append(f)

    
if __name__ == "__main__":
    wc = WebCrawler()
    wc.start("start_url")