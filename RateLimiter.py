import random
from threading import BoundedSemaphore, Lock, Semaphore, Thread
import time
import typing as T

CLIENTS = 3
MAX_TOKENS = 15

class TokenReplenisher(Thread):
    def __init__(self, name, client_to_tokens: dict[int, BoundedSemaphore]):
        super().__init__(name=name)
        self.client_to_tokens = client_to_tokens

    def _add_token(self, semaphore):
        try: 
            semaphore.release()
            print(f"TokenReplenisher added token.")
        except ValueError: 
            print(f"Cannot replenish tokens because we are at MAX.")
    
    def run(self):
        while True:
            # Create a copy/snapshot of the dictionary so that even if the dictionary changes, we do not error
            # This way, we do not have to lock the dictionary and wont impact the live requests
            token_buckets = list(self.client_to_tokens.values())
            for sem in token_buckets:
                self._add_token(sem)
            time.sleep(5)

class ShardedRateLimiter:
    def __init__(self, i):
        self.i = i 
        self.client_to_tokens: T.Dict[int, BoundedSemaphore] = {}
        self.token_replenisher = TokenReplenisher(f"TR-{i}", self.client_to_tokens)
        self.token_replenisher.start()

    def can_make_request(self, client):
        sem = self.client_to_tokens[client]
        acquired = sem.acquire(timeout=1)
        return acquired
    
    def add_client(self, client):
        self.client_to_tokens[client] = BoundedSemaphore(MAX_TOKENS)
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
        # if client not in self.client_to_tokens: 
        #     raise ValueError(f"Unregisted client {client}")
        if req_num:
            print(f"Client id {client} - request number {req_num}")

        rate_limiter = self._get_rate_limiter_for_client(client)
        acquired = rate_limiter.can_make_request(client)

        if not acquired: 
            raise ConnectionRefusedError(f"Client {client} has exceeded rate limits")
        else: 
            print(f"Client {client} made a request to server.")
            time.sleep(random.randint(1,5))


if __name__ == "__main__":
    server = RateLimitingServer()
    threads = []

    for client_num in range(CLIENTS):
        server.add_client(client_num)

    for i in range(CLIENTS): 
        for j in range(30):
            t = Thread(target=server.make_request, args=(i, j))
            t.start()
            threads.append(t)
    

        

