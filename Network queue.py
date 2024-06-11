import numpy as np
import heapq


class DESsim():
    def __init__(self, arrival_rate , service_rate, max_clock, transition_matrix) -> None:
        
        #initializing customers
        self.customers_in_system = [0]*len(transition_matrix)        
        
        #initialize variable for interarrival and service rate
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        
        #queue network
        self.transition_matrix = transition_matrix
        
        #handling events through priority
        self.event_queue = []
        self.queues = [{} for _ in range(len(transition_matrix))] #handling queues
        
                
        #initialize variable for clock
        self.current_time = 0
        self.last_event_time = 0
        self.max_clock = max_clock
        
        #initializaing arrival and departure
        # self.schedule_events(self.gen_interarrival_time(), 'Arrival', queue = 0)
        # self.depart_time = float('inf')
        
        #statistical counter
        self.num_arrivals = 0
        self.num_depart = 0
        #self.total_waiting_time = 0
        self.total_time_in_system = 0
        self.total_customer_in_system = 0
        self.total_time_in_service = [0] *len(transition_matrix)
        
        #initialize first arrival 
        for i in range(len(transition_matrix)):
            self.schedule_events(self.gen_interarrival_time(), 'Arrival', i)
        
        
        #self.master_queue = [(self.current_time , "Start")]
        
        
    #this is a scheduler
    def schedule_events(self, event_time, event_type, queue):
        heapq.heappush(self.event_queue, (event_time, event_type, queue))
        
    def clock(self): 
        while self.current_time < self.max_clock and self.event_queue:
            print(self.current_time)

            event_time, event_type, queue = heapq.heappop(self.event_queue)
            #self.master_queue.append((event_time, event_type, queue))
            
            #this sets the current time to the event time
            self.current_time = event_time        
            if event_type == "Arrival":
                self.handle_arrival_event(queue) 
            else:
                self.handle_departure_event(queue)
        
        self.logging()
                    
    def handle_arrival_event(self, queue):
        self.customers_in_system[queue] += 1
        self.num_arrivals += 1
        self.total_customer_in_system += 1
        
        self.arrival_time = self.current_time + self.gen_interarrival_time()
        self.schedule_events(self.arrival_time, "Arrival", queue) #adding events to the list
        
        if self.customers_in_system[queue] == 1:
            service_time = self.gen_service_time()
            self.total_time_in_service[queue] += service_time #logging 
            self.depart_time = self.current_time + service_time
            self.schedule_events(self.depart_time, "Departure", queue)
        
        
    def handle_departure_event(self, queue):
        self.customers_in_system[queue] -= 1
        self.num_depart += 1
        time_in_system = self.current_time - self.last_event_time
        self.total_time_in_system += time_in_system
        
        if self.customers_in_system[queue] > 0:
            service_time = self.gen_service_time()
            self.total_time_in_service[queue] += service_time
            self.depart_time = self.current_time + service_time
            self.schedule_events(self.depart_time, "Departure", queue)
        # else:
        #     self.depart_time = float('inf')
        #     #self.schedule_events(self.depart_time, "No customer for departure")
        
        next_queue = self.get_next_queue(queue)
        if next_queue is not None:
            self.schedule_events(self.current_time, "Arrival", next_queue)
        
        self.last_event_time = self.current_time
    
    def get_next_queue(self,current_queue):
        probabilities = self.transition_matrix[current_queue]
        next_queue = np.random.choice(len(probabilities), p=probabilities)
        return next_queue if probabilities[next_queue] > 0 else None
        
    def gen_interarrival_time(self,):
        
        scale_parameter = 1 / self.arrival_rate
        
        return np.random.exponential(scale= scale_parameter)
    
    def gen_service_time(self):
        
        scale_parameter = 1 / self.service_rate
        
        return np.random.exponential(scale=scale_parameter)
    
    def logging(self):
        
        #simulation statistics
        avg_num_in_system = sum(self.customers_in_system) / len(self.customers_in_system)
        avg_time_in_system = self.total_time_in_system / self.total_customer_in_system if self.total_customer_in_system > 0 else 0
        avg_time_in_service = sum(self.total_time_in_service) / self.total_customer_in_system if self.total_customer_in_system > 0 else 0
        avg_time_in_queue = avg_time_in_system - avg_time_in_service
        avg_num_in_queue = self.arrival_rate * avg_time_in_queue
        
        # Theoretical values
        theoretical_values = self.calculate_theoretical_values()
        
        print('Simulation results:')
        print(f'Average number of customers in system: {avg_num_in_system:.2f}')
        print(f'Average time spent in system: {avg_time_in_system:.2f}')
        print(f'Average time spent in queue: {avg_time_in_queue:.2f}')
        print(f'Average time spent in service: {avg_time_in_service:.2f}')
        print(f'Average number of customer in queue: {avg_num_in_queue:.2f}')

        print('\nTheoretical steady-state values:')
        for i, (L, L_q, W, W_q) in enumerate(theoretical_values):
            print(f'Queue {i}:')
            print(f'  Average number of customers in system: {L:.2f}')
            print(f'  Average number waiting in queue: {L_q:.2f}')
            print(f'  Average time spent in system: {W:.2f}')
            print(f'  Average time spent in queue: {W_q:.2f}')
    
    def calculate_theoretical_values(self):
        lambdas = np.zeros(len(self.transition_matrix))
        lambdas[0] = self.arrival_rate  # Assuming arrivals only happen at the first queue
        
        for _ in range(1000):  # Iterate to stabilize arrival rates
            lambdas = self.arrival_rate + np.dot(lambdas, self.transition_matrix)
        
        theoretical_values = []
        for i in range(len(self.transition_matrix)):
            lambda_i = lambdas[i]
            mu_i = self.service_rate
            rho_i = lambda_i / mu_i
            
            L_i = rho_i / (1 - rho_i)
            W_i = 1 / (mu_i - lambda_i)
            L_q_i = (rho_i ** 2) / (1 - rho_i)
            W_q_i = lambda_i / (mu_i * (mu_i - lambda_i))
            
            theoretical_values.append((L_i, L_q_i, W_i, W_q_i))
        
        return theoretical_values


if __name__=="__main__":
    transition_matrix = [
        [0.0, 0.0, 1],
        [0.0, 0.0, 1],
        [0.0, 0.0, 1]
    ]
    s = DESsim(10, 15, 10, transition_matrix)
    s.clock()
    print(f"customer in system: {s.customers_in_system}, arrival : {s.num_arrivals}, departure: {s.num_depart}") 