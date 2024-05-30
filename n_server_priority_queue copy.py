import numpy as np
import sys
import heapq
from collections import deque

class Sim():
    def __init__(self, lam_bda, mu, max_queue_length, num_servers, initial_customers, log: bool) -> None:
        self.total_customer_in_system = 0  # initially 0 customers
        self.lam_bda = lam_bda
        self.mu = mu
        self.max_queue_length = max_queue_length
        self.unsatisfied_customers = 0
        self.num_servers = num_servers #num of servers in system
        
        self.time = 0  # clock is 0
        self.event_queue = []  # priority queue for events
        
        if self.lam_bda>0:
            self.schedule_event(self.time + self.inter_arrival_gen(), 'arrival') #here scheduler is used
        
        
        #initialize server queues
        self.server_queues = [deque(maxlen=max_queue_length) for _ in range(num_servers)]
        self.server_status = ['idle']*num_servers
        
        #self.time_depart = [float('inf')]*self.num_servers
        
        #Allow customers to already be in the systems
        for _ in range(initial_customers):
            self.handle_initial_customer()
             
                
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

    def schedule_event(self, event_time, event_type, server_id=None):
        heapq.heappush(self.event_queue, (event_time, event_type, server_id))

    def sim_clock(self, max_clock):
        while self.time <= max_clock:
            if not self.event_queue: #if event queue is empty break the while
                break

            #logging
            self.time, event_type, server_id = heapq.heappop(self.event_queue) #from queue pop smallest time
            self.master_queue.append((self.time, event_type, server_id)) #log that time

            #print(f"time chosen: {self.time}, event: {event_type}")

            if event_type == 'arrival':
                self.arrival_event()
            elif event_type == 'departure':
                self.departure_event(server_id)
            elif event_type == 'abandon':
                self.abandon_event()

        self.logging()

    def arrival_event(self):
        self.total_num_arrived +=1 
        
        #first server with available space (using a for else loop)
        for server_id, queue in enumerate(self.server_queues):
            if len(queue) < self.max_queue_length:
                self.total_customer_in_system += 1
                queue.append(self.time)
                
                if len(queue) == 1 and self.server_status[server_id] == 'idle':
                    self.server_status[server_id] = 'busy'
                    self.schedule_event(self.time + self.service_time_gen(), 'departure', server_id)   
                break
        else:
            self.unsatisfied_customers += 1
        if self.lam_bda > 0:
            self.schedule_event(self.time + self.inter_arrival_gen(), 'arrival')
            

    def departure_event(self, server_id):
        queue = self.server_queues[server_id]
        
        if queue:
            queue.popleft()
            self.total_customer_in_system -= 1
            self.total_num_departed += 1

            self.customer_in_system.append(self.total_customer_in_system)
            self.num_departed.append(self.total_num_departed)
            self.event_selected.append("Departure")

            if queue:
                self.schedule_event(self.time + self.service_time_gen(), 'departure', server_id)
            else:
                self.server_status[server_id] = 'idle'
    
    def handle_initial_customer(self):
        for server_id, queue in enumerate(self.server_queues):
            if len(queue) < self.max_queue_length:
                self.total_customer_in_system += 1
                queue.append(self.time)
                if len(queue) == 1 and self.server_status[server_id] == 'idle':
                    self.server_status[server_id] = 'busy'
                    self.schedule_event(self.time + self.service_time_gen(), 'departure', server_id)
                break
        else:
            self.unsatisfied_customers += 1
    
    
    def max_waiting_time(self): #keep this hardcode for now change later to be adaptive
        return 10
                
    def abandon_event(self):
        for server_id, queue in enumerate(self.server_queues):
            if queue and self.time - queue[0] > self.max_waiting_time():
                queue.popleft()
                self.unsatisfied_customers += 1
                self.total_customer_in_system -= 1
                self.log_event("Abandon")
    
 
    def inter_arrival_gen(self):
        if self.lam_bda == 0:
            return float("inf")
        return np.random.exponential(1./self.lam_bda)  # Interarrival time
    
    
    def service_time_gen(self):
        if self.mu == 0:
            return float("inf")
        return np.random.exponential(1./self.mu)  # Service time 
    
    def log_event(self, event_type):
        self.event_selected.append(event_type)
        self.num_arrived.append(self.total_num_arrived)
        self.num_departed.append(self.total_num_departed)
        self.customer_in_system.append(self.total_customer_in_system)            

    
    def logging(self):
        if self.log:
            self.master_queue.append((self.time, "End of Simulation"))
            #print(self.dict)
            #print(f"Total unsatisfied customers: {self.unsatisfied_customers}")
            print(f"Master queue log: {self.master_queue}")
        #sys.exit("Simulation ended: simulation clock exceeds maximum clock time")

if __name__=="__main__":
    s = Sim(3,4, 2, 3,0, log=True)
    np.random.seed(0)
    for i in range(10):
        s.sim_clock(20)
