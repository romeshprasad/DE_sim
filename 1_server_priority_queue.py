import numpy as np
import sys
import heapq

class Sim():
    def __init__(self, lam_bda, mu, max_queue_length, num_servers, log: bool) -> None:
        self.total_customer_in_system = 0  # initially 0 customers
        self.lam_bda = lam_bda
        self.mu = mu
        self.max_queue_length = max_queue_length
        self.unsatisfied_customers = 0
        self.num_servers = num_servers #num of servers in system
        self.busy_server = 0
        self.time = 0  # clock is 0
        self.event_queue = []  # priority queue for events
        self.schedule_event(self.time + self.inter_arrival_gen(), 'arrival') #here scheduler is used
        self.time_depart = [float('inf')]*self.num_servers
        

        # statistics
        self.log = log
        # lists to keep track of events
        self.num_arrived = []
        self.num_departed = []
        self.waiting_time = []
        self.event_selected = []
        self.customer_in_system = []

        # total counts
        self.total_num_arrived = 0
        self.total_num_departed = 0

        # dictionary to store all statistics
        self.dict = {
            'event type': self.event_selected,
            'customer arrived': self.num_arrived,
            'customer_in_system': self.customer_in_system,
            'customer_departed': self.num_departed,
        }

        # initialize master queue
        self.master_queue = [(0, 'start')]

    def schedule_event(self, event_time, event_type):
        heapq.heappush(self.event_queue, (event_time, event_type))

    def sim_clock(self, max_clock):
        while self.time <= max_clock:
            if not self.event_queue: #if event queue is empty break the while
                break

            #logging
            self.time, event_type = heapq.heappop(self.event_queue) #from queue pop smallest time
            self.master_queue.append((self.time, event_type)) #log that time

            #print(f"time chosen: {self.time}, event: {event_type}")

            if event_type == 'arrival':
                self.arrival_event()
            else:
                self.departure_event()

        self.logging()

    def arrival_event(self):
        if self.total_customer_in_system <= self.max_queue_length*self.num_servers:
            self.total_customer_in_system += 1
            self.total_num_arrived += 1

            self.num_arrived.append(self.total_num_arrived)
            self.event_selected.append("Arrival")
            self.customer_in_system.append(self.total_customer_in_system)
            
            #this logic checks if server is busy
            if self.busy_server < self.num_servers:
                self.busy_server += 1
                for i in range(self.num_servers):
                    if self.time_depart[i] == float("inf"):
                        self.schedule_event(self.time + self.service_time_gen(), 'departure')
                        break
            # if self.total_customer_in_system == 1:
            #     self.schedule_event(self.time + self.service_time_gen(), 'departure')
            
            self.schedule_event(self.time + self.inter_arrival_gen(), 'arrival')
        else:
            self.unsatisfied_customers += 1
            self.schedule_event(self.time + self.inter_arrival_gen(), 'arrival')
        
        #print(f"Server status: {'Busy' if self.total_customer_in_system > 0 else 'Idle'}")

    def departure_event(self):
        self.total_customer_in_system -= 1
        self.total_num_departed += 1

        self.customer_in_system.append(self.total_customer_in_system)
        self.num_departed.append(self.total_num_departed)
        self.event_selected.append("Departure")
        
        for i in range(self.num_servers):
            if self.time == self.time_depart[i]:
                self.time_depart[i] = float('inf')
                break

        self.busy_server -= 1
        if self.total_customer_in_system >= self.num_servers:
            self.busy_server += 1
            for i in range(self.num_servers):
                if self.time_depart[i] == float('inf'):
                    self.schedule_event(self.time + self.service_time_gen(), 'departure')
                    #self.time_depart[i] = self.time + self.service_time_gen()
                    break

        # if self.total_customer_in_system > 0:
        #     self.busy_server -= 1
        #     if 
        #     self.schedule_event(self.time + self.service_time_gen(), 'departure')

        #print(f"Server status: {'Busy' if self.total_customer_in_system > 0 else 'Idle'}")

    def inter_arrival_gen(self):
        return np.random.exponential(1./self.lam_bda)  # Interarrival time
    
    def service_time_gen(self):
        return np.random.exponential(1./self.mu)  # Service time 
    
    def logging(self):
        if self.log:
            self.master_queue.append((self.time, "End of Simulation"))
            #print(self.dict)
            #print(f"Total unsatisfied customers: {self.unsatisfied_customers}")
            print(f"Master queue log: {self.master_queue}")
        sys.exit("Simulation ended: simulation clock exceeds maximum clock time")

if __name__=="__main__":
    s = Sim(3,4, 5, 1, log=True)
    np.random.seed(0)
    for i in range(1000):
        s.sim_clock(20)
