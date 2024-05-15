import numpy as np
import sys
"""
yet to do : server is busy or idle, capacity of the waiting line, simulation end time
"""

class sim():
    def __init__(self, lam_bda, mu, log:bool) -> None:
        self.total_customer_in_system = 0 #initially 0 customers
        self.lam_bda = lam_bda
        self.mu = mu

        self.time = 0 #clock is 0
        self.time_arrival = self.inter_arrival_gen()
        self.time_depart = float('inf')
        
        #statitiscs
        """
        Keep a track of number of customers arrived, number of customers departed and total waiting time

        """
        self.log = log
        # list
        self.num_arrived = []
        self.num_departed = []
        self.waiting_time = []
        self.event_selected = []
        self.customer_in_system = []

        #total count
        self.total_num_arrived = 0
        self.total_num_departed = 0
        self.total_waiting_time = 0

        #dictionary
        self.dict = {'event type': self.event_selected, 'customer arrived': self.num_arrived,
                     'customer_in_system': self.customer_in_system, 
                     'customer_departed': self.num_departed,
                     'waiting_time' : self.waiting_time} 


    def clock(self, max_clock):
        """
        t_event -> Scanning event list to determine which next event to move the clock forward 
        In this example: [FIFO]
        """
        t_event = min(self.time_arrival, self.time_depart)
        
        self.waiting_time.append(t_event - self.time)

        self.total_waiting_time += self.total_customer_in_system*(t_event - self.time)

        self.time = t_event
        print(f"time choosen : {self.time} arrival time {self.time_arrival} departure time : {self.time_depart}")

        if self.time <= max_clock: #End simulation if it exceeds the max length of simulation
            if self.time_arrival < self.time_depart:
                self.arrival_event()
            else:
                self.departure_event()
        else:
            self.logging()

    def arrival_event(self):
        self.total_customer_in_system += 1
        self.total_num_arrived += 1
        
        self.num_arrived.append(self.total_num_arrived)
        self.event_selected.append("Arrival")
        self.customer_in_system.append(self.total_customer_in_system)


        if self.total_customer_in_system <= 1:
            self.time_depart = self.time + self.service_time_gen() #for the first arrival
        self.time_arrival = self.time + self.inter_arrival_gen()    #arrival time
        #print(f"arrival time", self.time_arrival)
    
    def departure_event(self):
        self.total_customer_in_system -= 1
        self.total_num_departed += 1

        self.customer_in_system.append(self.total_customer_in_system)
        self.num_arrived.append(self.total_num_departed)
        self.event_selected.append("Departure")
        
        if self.total_customer_in_system > 0 :
            self.time_depart = self.time + self.service_time_gen() #time for departure 
        else:
            self.time_depart = float('inf') 
        #idle time
        #print(f"arrival time", self.time_depart)      
    
    def inter_arrival_gen(self):
        
        return np.random.exponential(1./self.lam_bda) #Interarrival time
    
    def service_time_gen(self):

        return np.random.exponential(1./self.mu) #service time 
    
    def logging(self):
        if self.log == True:
            print(self.dict)
        sys.exit("Simulation ended: simulation clock exceeds maximum clock time")
        


if __name__=="__main__":
    s = sim(3,4, log=True)
    np.random.seed(0)
    for i in range(1000):
        s.clock(5)
        