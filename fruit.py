from ray import serve

from ray.serve.metrics import Counter, Gauge, Histogram
from starlette.requests import Request
import logging
import time
import psutil

logger = logging.getLogger("ray.serve")


@serve.deployment(num_replicas=1)
class FruitMarket:
    def __init__(self):
        name = 'fruit_market'
        logger.info("Initializing Logs for Ray serve... setting up Metrics")
        self.counter = Counter(
            "num_prime_requests",
            description="Number of prime request processed by the serving.",
            tag_keys=("deployment_name",),
        )
        self.counter.set_default_tags({"deployment_name": name})

        self.gauge = Gauge(
            "curr_prime_count_mem_usage",
            description="Current count of prime request memory usage. Goes up and down.",
            tag_keys=("deployment_name",),
        )
        self.gauge.set_default_tags({"deployment_name": name})

        self.histogram = Histogram(
            "prime_request_latency",
            description="Latencies of prime requests in ms.",
            boundaries=[0.1, 1],
            tag_keys=("deployment_name",),
        )
        self.histogram.set_default_tags({"deployment_name": name})

    async def check_prime(self, fruit: str, amount: int) -> str:
        start = time.time()
        if amount < 2:
            return f"fruit {fruit} is sold at non prime prize {amount}"
        i = 2
        while i * i <= amount:
            if amount % i == 0:
                return f"fruit {fruit} is sold at non prime prize {amount}"
            i += 1
        # Increment the total request count.
        self.counter.inc()
        # Update the gauge to the new value.

        process = psutil.Process()
        self.gauge.set(process.memory_info().rss)
        # Record the latency for this request in ms.
        self.histogram.observe(1000 * (time.time() - start))
        return f"fruit {fruit} is sold at prime prize {amount} ... congratulation"

    async def __call__(self, request: Request) -> str:
        payload = await request.json()
        amount = payload['amount']
        fruit = payload['fruit']
        if isinstance(amount, int):
            return await self.check_prime(fruit, amount)
        else:
            logger.info(f"Amount {amount} is non numeric ... skipping it")
            return f"Amount `{amount}` is not a number !!! "


deployment_graph = FruitMarket.bind()
