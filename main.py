import numpy as np

class sim():
    def __init__(self) -> None:
        self.customer_in_system = 0 #initially 0 customers
        

        self.time = 0 #clock is 0
        self.time_arrival = self.inter_arrival_gen()
        self.time_depart = float('inf')
        
        #statitiscs
        """
        Keep a track of number of customers arrived, number of customers departed and total waiting time
        """
        
        self.num_arrived = 0
        self.num_departed = 0
        self.total_waiting_time = 0


    def clock(self):
        t_event = min(self.time_arrival, self.time_depart) #FIFO
        self.total_waiting_time += self.customer_in_system*(t_event - self.time)

        self.time = t_event

        if self.time_arrival < self.time_depart:
            self.arrival_event()
        else:
            self.departure_event()

    def arrival_event(self):
        self.customer_in_system += 1
        self.num_arrived += 1
        if self.num_arrived <= 1:
            self.time_depart = self.time + self.service_time_gen()
        self.time_arrival = self.time + self.inter_arrival_gen()    
        
    
    def departure_event(self):
        self.customer_in_system -= 1
        self.num_departed += 1
        if self.customer_in_system > 0 :
            self.time_depart = self.clock + self.service_time_gen()
        else:
            self.time_depart = float('inf')        
    
    def inter_arrival_gen(self):
        
        return np.random.exponential(1/3) #Assuming a salon shop and on an average 3 customers arrive in an hour
    
    def service_time_gen(self):

        return np.random.exponential(1/2) #Assuming a service time of 2 customer per hour 
    
if __name__=="__main__":
    s = sim()
    np.random.seed(0)
    for i in range(1):
        s.clock()