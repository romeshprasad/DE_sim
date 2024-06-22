import numpy as np
from server import Server

class Queue:
    def __init__(self, queue_id, num_servers, service_rate):
        self.queue_id = queue_id
        self.servers = [Server(i) for i in range(num_servers)]
        self.service_rate = service_rate
        self.queue = []  # Queue of agents waiting to be served

    def generate_service_time(self):
        # Generate service time using exponential distribution
        return round(np.random.exponential(1.0 / self.service_rate),3)