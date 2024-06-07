import numpy as np
import heapq


class DESsim():
    def __init__(self, arrival_rate , service_rate) -> None:
        #initializing customers
        self.customers_in_system = 0        
        #initialize variable for interarrival and service rate
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        
        #handling events through priority
        self.event_queue = []
        
        #initialize variable for clock
        self.current_time = 0
        self.last_event_time = 0
        
        #initializaing arrival and departure
        self.schedule_events(self.gen_interarrival_time(), 'Arrival')
        self.depart_time = float('inf')
        
        #statistical counter
        self.num_arrivals = 0
        self.num_depart = 0
        #self.total_waiting_time = 0
        self.total_time_in_system = 0
        self.total_customer_in_system = 0
        self.total_time_in_service = 0
        self.master_queue = [(self.current_time , "Start")]
        

    #this is a scheduler
    def schedule_events(self, event_time, event_type):
        heapq.heappush(self.event_queue, (event_time, event_type))
        
    def clock(self, max_clock): 
        while self.current_time < max_clock:
            print(self.current_time)
            #this give us the total waiting time
            #event_time = min(self.arrival_time, self.depart_time)
            #self.total_waiting_time += self.customers_in_system*(event_time - self.current_time)
            event_time, event_type = heapq.heappop(self.event_queue)
            self.master_queue.append((event_time, event_type))
            
            #this sets the current time to the event time
            self.current_time = event_time


        
            if event_type == "Arrival":
                self.handle_arrival_event() 
            else:
                self.handle_departure_event()
        
    
        #simulation statistics
        avg_num_in_system = self.total_time_in_system / self.current_time if self.current_time > 0 else 0
        avg_time_in_system = self.total_time_in_system / self.total_customer_in_system if self.total_customer_in_system > 0 else 0
        avg_time_in_service = self.total_time_in_service / self.total_customer_in_system if self.total_customer_in_system > 0 else 0
        avg_time_in_queue = avg_time_in_system - avg_time_in_service
        avg_num_in_queue = self.arrival_rate * avg_time_in_queue
        
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
        print(f'Average number of customer in queue: {avg_num_in_queue:.2f}')

        print('\nTheoretical steady-state values:')
        print(f'Average number of customers in system: {L:.2f}')
        print(f"Average number waiting in queue: {L_q:.2f}")
        print(f'Average time spent in system: {W:.2f}')
        print(f'Average time spent in queue: {W_q:.2f}')
        print(f'Average time spent in service: {1 / self.service_rate:.2f}')
                
    def handle_arrival_event(self):
        self.customers_in_system += 1
        self.num_arrivals += 1
        self.total_customer_in_system += 1
        
        if self.customers_in_system == 1:
            service_time = self.gen_service_time()
            self.total_time_in_service += service_time #logging 
            self.depart_time = self.current_time + service_time
            self.schedule_events(self.depart_time, "Departure")
        
        self.arrival_time = self.current_time + self.gen_interarrival_time()
        self.schedule_events(self.arrival_time, "Arrival") #adding events to the list
        
    def handle_departure_event(self):
        self.customers_in_system -= 1
        self.num_depart += 1
        time_in_system = self.current_time - self.last_event_time
        self.total_time_in_system += time_in_system
        
        if self.customers_in_system > 0:
            self.depart_time = self.current_time + self.gen_service_time()
            self.schedule_events(self.depart_time, "Departure")
        else:
            self.depart_time = float('inf')
            #self.schedule_events(self.depart_time, "No customer for departure")
        
        self.last_event_time = self.current_time
    
    def gen_interarrival_time(self,):
        
        scale_parameter = 1 / self.arrival_rate
        
        return np.random.exponential(scale= scale_parameter)
    
    def gen_service_time(self):
        
        scale_parameter = 1 / self.service_rate
        
        return np.random.exponential(scale=scale_parameter)
    
    
if __name__=="__main__":
    s = DESsim(10,15)
    
    s.clock(5000)
    print(f"customer in system: {s.customers_in_system}, arrival : {s.num_arrivals}, departure: {s.num_depart}")
    #print(f"avg_customer in system: {}, ")    