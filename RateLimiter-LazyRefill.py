from concurrent.futures import ThreadPoolExecutor
import random
from threading import BoundedSemaphore, Lock, Semaphore, Thread
import time
import typing as T

CLIENTS = 3
MAX_TOKENS = 15
RATE_OF_REFILL = 1 # 1 per second


class TokenBucket:
    def __init__(self, client):
        self.client = client
        self._lock = Lock()
        self.tokens = MAX_TOKENS
        self.last_refilled = time.time()

    def can_make_request(self):
        with self._lock:
            print(f"Tokens for {self.client} before refill: {self.tokens}")
            now = time.time()
            time_elapsed_seconds = now - self.last_refilled
            self.tokens = min(MAX_TOKENS, self.tokens + time_elapsed_seconds * RATE_OF_REFILL)
            self.last_refilled = now
            print(f"Tokens for {self.client} after refill: {self.tokens}")

            if 1 <= self.tokens:
                self.tokens -= 1
                print(f"Tokens for {self.client} after consuming: {self.tokens}")
                return True
            print(f"Client {self.client} rejected, tokens={self.tokens}")
            return False

class ShardedRateLimiter:
    def __init__(self, i):
        self.i = i 
        self.client_to_tokens: T.Dict[int, TokenBucket] = {}

    def can_make_request(self, client):
        token_bucket = self.client_to_tokens[client]
        return token_bucket.can_make_request()
    
    def add_client(self, client):
        self.client_to_tokens[client] = TokenBucket(client)
        print(f"Added {client} to Sharded Rate Limiter {self.i}")

class RateLimitingServer:
    def __init__(self):
        self.rate_limiters = []
        for i in range(5):
            self.rate_limiters.append(ShardedRateLimiter(i))

    def _get_rate_limiter_for_client(self, client) -> ShardedRateLimiter:
        num_rate_limiters = len(self.rate_limiters)
        rl_id = hash(client) % num_rate_limiters
        print(f"Rate Limiter {rl_id} retrieved for {client}")
        return self.rate_limiters[rl_id]

    def add_client(self, client):
        rl = self._get_rate_limiter_for_client(client)
        rl.add_client(client)
        
    def make_request(self, client, req_num=None):
        if req_num is not None:
            print(f"Client id {client} - request number {req_num}")

        rate_limiter = self._get_rate_limiter_for_client(client)
        acquired = rate_limiter.can_make_request(client)

        if not acquired: 
            raise ConnectionRefusedError(f"Client {client} has exceeded rate limits")
        else: 
            print(f"Client {client} made a request to server.")
            # time.sleep(random.randint(1,5))
            return f"{client}-{req_num}"


if __name__ == "__main__":
    server = RateLimitingServer()
    # threads = []

    # for client_num in range(CLIENTS):
    #     server.add_client(client_num)

    # futures = []
    # with ThreadPoolExecutor(max_workers=20) as executor:
    #     for client_id in range(CLIENTS): 
    #         for j in range(30): 
    #             futures.append(
    #                 executor.submit(server.make_request, client_id, j)
    #             )

    # for future in futures:
    #     try:
    #         print(f"Future result: {future.result()}")
    #     except ConnectionRefusedError:
    #         print("Rate limit exceeded (expected)")

    # Tests

    server.add_client(1)

    for i in range(MAX_TOKENS):
        server.make_request(client=1, req_num=i)
    assert(server._get_rate_limiter_for_client(1).client_to_tokens[1].tokens < 1)

    # Next request fails
    try:
        server.make_request(1, 100)
    except ConnectionRefusedError as e: 
        print("Correctly failed")

    # Lazy refill test
    time.sleep(2)

    for i in range(2):
        server.make_request(client=1, req_num=i)
    assert(server._get_rate_limiter_for_client(1).client_to_tokens[1].tokens < 1)

        

