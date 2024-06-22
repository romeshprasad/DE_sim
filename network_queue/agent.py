import numpy as np

class Agent:
    def __init__(self, arrival_time, agent_id):
        self.arrival_time = arrival_time
        self.service_start_time = None
        self.departure_time = None
        self.queue_length_on_arrival = None
        self.server_id = None
        self.agent_id = agent_id  # Unique identifier for the agent

    def __lt__(self, other):
        return self.arrival_time < other.arrival_time