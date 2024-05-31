import heapq
import numpy as np
from collections import deque

class SeriesSystemSim:
    def __init__(self, lam_bda, service_rates, max_queue_length, log: bool) -> None:
        self.lam_bda = lam_bda
        self.service_rates = service_rates
        self.max_queue_length = max_queue_length
        self.num_processes = len(service_rates)
        self.log = log

        self.time = 0
        self.total_num_arrived = 0
        self.total_num_departed = 0
        self.total_customer_in_system = 0
        self.unsatisfied_customers = 0

        self.event_queue = []
        self.queues = [deque(maxlen=max_queue_length) for _ in range(self.num_processes)]
        self.server_status = ['idle'] * self.num_processes

        # Statistics
        self.num_arrived = []
        self.num_departed = []
        self.waiting_time = []
        self.event_selected = []
        self.customer_in_system = []
        
        #logging into a master queue
        self.master_queue = [(0, 'start')]

        # Schedule the first arrival event
        self.schedule_event(self.inter_arrival_gen(), 'arrival')

    def inter_arrival_gen(self):
        return np.random.exponential(1.0 / self.lam_bda)

    def service_time_gen(self, process_index):
        return np.random.exponential(1.0 / self.service_rates[process_index])

    def schedule_event(self, event_time, event_type, process_index=None):
        heapq.heappush(self.event_queue, (event_time, event_type, process_index))

    def clock(self, max_clock):
        while self.event_queue:
            
            event_time, event_type, process_index = heapq.heappop(self.event_queue)
            self.master_queue.append((self.time, event_type, process_index)) #log that time
            
            if event_time > max_clock:
                break
            self.time = event_time
            if event_type == 'arrival':
                self.handle_arrival()
            elif event_type == 'departure':
                self.handle_departure(process_index)
        if self.log:
            self.log_statistics()

    def handle_arrival(self):
        self.total_num_arrived += 1

        # Check if the first process queue is full
        if len(self.queues[0]) >= self.max_queue_length:
            self.unsatisfied_customers += 1
            self.log_event("Rejected Arrival")
        else:
            self.total_customer_in_system += 1
            self.queues[0].append(self.time)  # Customer arrives at the first process
            self.log_event("Arrival")

            if self.server_status[0] == 'idle':
                self.server_status[0] = 'busy'
                self.schedule_event(self.time + self.service_time_gen(0), 'departure', 0)  # Schedule departure from the first process

        self.schedule_event(self.time + self.inter_arrival_gen(), 'arrival')

    def handle_departure(self, process_index):
        arrival_time = self.queues[process_index].popleft()
        wait_time = self.time - arrival_time
        self.waiting_time.append(wait_time)

        if process_index < self.num_processes - 1:
            # Check if the next process queue is full
            if len(self.queues[process_index + 1]) >= self.max_queue_length:
                self.unsatisfied_customers += 1
                self.log_event(f"Rejected at Process {process_index + 1}")
            else:
                self.queues[process_index + 1].append(self.time)  # Move customer to the next process
                self.log_event(f"Departure from Process {process_index + 1}")

                if self.server_status[process_index + 1] == 'idle':
                    self.server_status[process_index + 1] = 'busy'
                    self.schedule_event(self.time + self.service_time_gen(process_index + 1), 'departure', process_index + 1)
        else:
            self.total_customer_in_system -= 1
            self.total_num_departed += 1
            self.log_event("Departure from System")

        if self.queues[process_index]:
            self.schedule_event(self.time + self.service_time_gen(process_index), 'departure', process_index)
        else:
            self.server_status[process_index] = 'idle'

    def log_event(self, event_type):
        self.event_selected.append(event_type)
        self.num_arrived.append(self.total_num_arrived)
        self.num_departed.append(self.total_num_departed)
        self.customer_in_system.append(self.total_customer_in_system)

    def log_statistics(self):
        statistics = {
            'event type': self.event_selected,
            'customer arrived': self.num_arrived,
            'customer_in_system': self.customer_in_system,
            'customer_departed': self.num_departed,
            'waiting_time': self.waiting_time
        }
        print(self.master_queue)
        print(statistics)
        print(f"Total Customers Arrived: {self.total_num_arrived}")
        print(f"Total Customers Departed: {self.total_num_departed}")
        print(f"Total Unsatisfied Customers: {self.unsatisfied_customers}")

if __name__ == "__main__":
    np.random.seed(0)
    service_rates = [4, 5, 3]  # Example service rates for 3 processes
    max_queue_length = 5  # Example max queue length for each process
    sim = SeriesSystemSim(lam_bda=3, service_rates=service_rates, max_queue_length=max_queue_length, log=True)
    sim.clock(max_clock=100)
