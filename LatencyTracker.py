# Design a latency tracker class to handle the following functionalities: 
# 1. Store latency samples. 
# Input includes: timestamp, latency in milliseconds. 
# 
# 2. Query the specified percentile latency within a given time window. 
# Input includes: time window, percentile. 
# 
# The class needs to support concurrency.


# Questions
# 1. Do we need to store the latency information forever and on the fly compute? yes 
# 2. Will the latency information come in order of timestamp? i.e. requests that come later will always have later timestamps? 
# 3. Will we be able to hold all of the data in memory? 
# 4. Fixed time windows? 

import bisect
from collections import deque
from threading import Lock

from sortedcontainers import SortedDict, SortedList


class LatencyTracker: 
    def __init__(self):
        self.events = SortedList()
        self._lock = Lock()

    def store_latency(self, timestamp, latency):
        with self._lock:
            self.events.add((timestamp, latency))

    def get_percentile_latency(self, time_window, percentile):
        with self._lock:
            start, end = time_window
            left = bisect.bisect_left(self.events, start)
            right = bisect.bisect_right(self.events, end)

            latencies = [x[1] for x in self.events[left:right]]

            sorted_latencies = sorted(latencies)
            k = percentile * (len(sorted_latencies)-1) / 100
            if k == int(k):
                return sorted_latencies[k]
            f = int(k)
            c = min(f+1, len(sorted_latencies)-1)

            d0 = sorted_latencies[f] * (c - k)
            d1 = sorted_latencies[c] * (k - f)

            return d0 + d1