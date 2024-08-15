import random
from math import gcd

class RandomOrderGenerator:
    def __init__(self, start, end):
        self.n = end - start
        self.start = start
        self.a = self.find_coprime_a()
        self.b = random.randint(0, self.n-1)
        self.current_x = 0

    def find_coprime_a(self):
        # Try to find a coprime number in [n/2, n) and limit the search to 100,000 attempts to ensure fast execution
        attempts = 0
        while attempts < 1000000:
            candidate = random.randint(self.n // 2, self.n - 1)
            if gcd(candidate, self.n) == 1:
                return candidate
            attempts += 1
        raise ValueError("Failed to find a coprime number within 1,000,000 attempts")

    def next_value(self):
        if self.current_x >= self.n:
            raise StopIteration("All values have been visited")
        value = (self.a * self.current_x + self.b) % self.n
        self.current_x += 1
        return self.start + value

    def reset(self):
        self.current_x = 0
        self.b = random.randint(0, self.n-1)
