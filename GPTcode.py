import heapq
import random
import numpy as np

class Event:
    def __init__(self, time, event_type):
        self.time = time
        self.event_type = event_type

    def __lt__(self, other):
        return self.time < other.time

class MM1Queue:
    def __init__(self, arrival_rate, service_rate, max_time):
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.max_time = max_time

        self.clock = 0
        self.num_in_system = 0
        self.total_customers = 0
        self.total_time_in_system = 0
        self.total_time_in_queue = 0
        self.total_time_in_service = 0
        self.last_event_time = 0
        self.queue = []

        self.event_queue = []
        heapq.heappush(self.event_queue, Event(self.generate_interarrival_time(), 'arrival'))

    def generate_interarrival_time(self):
        return random.expovariate(self.arrival_rate)

    def generate_service_time(self):
        return random.expovariate(self.service_rate)

    def process_arrival(self, event):
        self.clock = event.time
        self.num_in_system += 1
        self.total_customers += 1

        heapq.heappush(self.event_queue, Event(self.clock + self.generate_interarrival_time(), 'arrival'))
        
        if self.num_in_system == 1:
            service_time = self.generate_service_time()
            self.total_time_in_service += service_time
            heapq.heappush(self.event_queue, Event(self.clock + service_time, 'departure'))

    def process_departure(self, event):
        self.clock = event.time
        self.num_in_system -= 1
        time_in_system = self.clock - self.last_event_time
        self.total_time_in_system += time_in_system

        if self.num_in_system > 0:
            service_time = self.generate_service_time()
            self.total_time_in_service += service_time
            heapq.heappush(self.event_queue, Event(self.clock + service_time, 'departure'))

        self.last_event_time = self.clock

    def simulate(self):
        while self.event_queue and self.clock < self.max_time:
            event = heapq.heappop(self.event_queue)
            if event.event_type == 'arrival':
                self.process_arrival(event)
            elif event.event_type == 'departure':
                self.process_departure(event)

        avg_num_in_system = self.total_time_in_system / self.clock if self.clock > 0 else 0
        avg_time_in_system = self.total_time_in_system / self.total_customers if self.total_customers > 0 else 0
        avg_time_in_service = self.total_time_in_service / self.total_customers if self.total_customers > 0 else 0
        avg_time_in_queue = avg_time_in_system - avg_time_in_service

        # Theoretical values
        rho = self.arrival_rate / self.service_rate
        L = rho / (1 - rho)
        W = 1 / (self.service_rate - self.arrival_rate)
        L_q = (rho ** 2) / (1 - rho)
        W_q = self.arrival_rate / (self.service_rate * (self.service_rate - self.arrival_rate))

        print('Simulation results:')
        print(f'Average number of customers in system: {avg_num_in_system:.2f}')
        print(f'Average time spent in system: {avg_time_in_system:.2f}')
        print(f'Average time spent in queue: {avg_time_in_queue:.2f}')
        print(f'Average time spent in service: {avg_time_in_service:.2f}')

        print('\nTheoretical steady-state values:')
        print(f'Average number of customers in system: {L:.2f}')
        print(f'Average time spent in system: {W:.2f}')
        print(f'Average time spent in queue: {W_q:.2f}')
        print(f'Average time spent in service: {1 / self.service_rate:.2f}')

if __name__ == "__main__":
    arrival_rate = 10  # Lambda
    service_rate = 15  # Mu
    max_time = 1000000  # Simulation end time (increased for better approximation)

    mm1 = MM1Queue(arrival_rate, service_rate, max_time)
    mm1.simulate()
