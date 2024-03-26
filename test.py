import ray
ray.init()


@ray.remote(num_cpus=0.5)
class Counter:
    def __init__(self):
        # Used to verify runtimeEnv
        self.name = "AIP Rocks"
        self.counter = 0
    def inc(self):
        self.counter += 1
    def get_counter(self):
        return "{} got {}".format(self.name, self.counter)

counter = Counter.remote()

for _ in range(5):
    ray.get(counter.inc.remote())
    print(ray.get(counter.get_counter.remote()))
