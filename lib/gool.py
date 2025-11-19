import concurrent.futures
import os
import queue
import threading
import typing


class Wait:
    # A simple implementation of a wait group similar to Go's sync.WaitGroup.

    def __init__(self) -> None:
        # Initialize the wait group with a count of zero and an event.
        self.count = 0
        self.event = threading.Event()
        self.mutex = threading.Lock()

    def add(self, n: int) -> None:
        # Increment the count of tasks to wait for.
        with self.mutex:
            self.count += n

    def done(self) -> None:
        # Decrement the count of tasks and set the event if count reaches zero.
        with self.mutex:
            self.count -= 1
            if self.count == 0:
                self.event.set()

    def wait(self) -> None:
        # Block until the count reaches zero.
        self.event.wait()


class Func:
    # A wrapper for a callable that integrates with the Wait mechanism.
    def __init__(self, f: typing.Callable, q: queue.Queue, w: Wait) -> None:
        self.f = f
        self.q = q
        self.w = w
        self.q.put(0)
        self.w.add(1)

    def __call__(self, *args, **kwargs) -> None:
        self.f(*args, **kwargs)
        self.q.get()
        self.w.done()


class Gool:
    # A pool of worker threads that can execute tasks concurrently.

    cpuq = queue.Queue(min(32, (os.process_cpu_count() or 1) + 4))

    def __init__(self, e: concurrent.futures.Executor, q: queue.Queue, w: Wait) -> None:
        self.e = e
        self.q = q
        self.w = w

    def call(self, func, *args, **kwargs) -> concurrent.futures.Future:
        # Submit a task to the pool, wrapping it with Func to manage completion.
        return self.e.submit(Func(func, self.q, self.w), *args, **kwargs)

    def wait(self) -> None:
        # Wait for all submitted tasks to complete.
        self.w.wait()
        self.e.shutdown()


def max(n: int) -> Gool:
    # Create a Gool with a maximum of n concurrent workers.
    limits = queue.Queue(n)
    worker = n
    return Gool(concurrent.futures.ThreadPoolExecutor(max_workers=worker), limits, Wait())


def cpu() -> Gool:
    # Create a Gool that uses a thread pool with a number of workers equal to the CPU count.
    limits = Gool.cpuq
    worker = Gool.cpuq.maxsize
    return Gool(concurrent.futures.ThreadPoolExecutor(max_workers=worker), limits, Wait())
