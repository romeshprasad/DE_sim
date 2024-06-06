import numpy as np


class DESsim():
    def __init__(self, lam_bda , mu) -> None:
        #initializing customers
        self.customers_in_system = 0        
        #initialize variable for interarrival and service rate
        self.lam_bda = lam_bda
        self.mu = mu
        
        #initialize variable for clock
        self.current_time = 0
        
        #initializaing arrival and departure
        self.arrival_time = self.gen_interarrival_time()
        self.depart_time = float('inf')
        
        #statistical counter
        self.num_arrivals = 0
        self.num_depart = 0
        self.total_waiting_time = 0
    
    def clock(self):
        
        #this give us the total waiting time
        event_time = min(self.arrival_time, self.depart_time)
        self.total_waiting_time += self.customers_in_system*(event_time - self.current_time)
        
        self.current_time = event_time
        
        
        if self.arrival_time <= self.depart_time:
            self.handle_arrival_event() 
        else:
            self.handle_departure_event()
        #print(f"customer in system: {s.customers_in_system}, arrival : {s.num_arrivals}, departure: {s.num_depart}, waiting time: {s.total_waiting_time}")
                
    def handle_arrival_event(self):
        self.customers_in_system += 1
        self.num_arrivals += 1
        
        if self.customers_in_system <= 1:
            self.depart_time = self.current_time + self.gen_service_time()
        self.arrival_time = self.current_time + self.gen_interarrival_time()
        
    
    def handle_departure_event(self):
        self.customers_in_system -= 1
        self.num_depart += 1
        
        if self.customers_in_system > 0:
            self.depart_time = self.current_time + self.gen_service_time()
        else:
            self.depart_time = float('inf')
    
    def gen_interarrival_time(self,):
        
        scale_parameter = 1 / self.lam_bda
        
        return np.random.exponential(scale= scale_parameter)
    
    def gen_service_time(self):
        
        scale_parameter = 1 / self.mu
        
        return np.random.exponential(scale=scale_parameter)
    
    
if __name__=="__main__":
    s = DESsim(10,15)
    for i in range(5000):
        s.clock()
    print(f"customer in system: {s.customers_in_system}, arrival : {s.num_arrivals}, departure: {s.num_depart}, waiting time: {s.total_waiting_time}, average_waiting_time: {s.total_waiting_time / s.num_depart}")
    
        
    