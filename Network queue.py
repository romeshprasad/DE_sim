import numpy as np
import heapq
import matplotlib.pyplot as plt
import networkx as nx

class DESsim():
    def __init__(self, arrival_rate, service_rate, max_clock, transition_matrix) -> None:
        
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
        
        #initialize arrival and departure
        # self.schedule_events(self.gen_interarrival_time(), 'Arrival', queue = 0)
        # self.depart_time = float('inf')
        
        #statistical counter
        self.num_arrivals = 0
        self.num_depart = 0
        self.total_time_in_system = 0
        self.total_customer_in_system = 0
        self.total_time_in_service = [0] * len(transition_matrix)
        
        #initialize first arrival 
        for i in range(len(transition_matrix)):
            self.schedule_events(self.gen_interarrival_time(), 'Arrival', i)
        
        #agent counter 
        self.customer = 0
        self.data = {}
        
        self.customer_movements = []
        
        self.graph = nx.DiGraph()
        for i in range(len(transition_matrix)):
            for j in range(len(transition_matrix[i])):
                if transition_matrix[i][j] > 0:
                    self.graph.add_edge(i, j)
        
        
    
    #this is a scheduler
    def customer_id(self):
        self.customer += 1
        return self.customer

    def fetch_data(self, header=True):
        '''
        It is going to take data from queue
                Parameters
        ----------
        return_header : bool (optonal, default: ``False``)
            Determines whether the column headers are returned.

        Returns
        -------
        data : :class:`~numpy.ndarray`
            A six column :class:`~numpy.ndarray` of all the data. The
            columns are:

            * 1st: The arrival time of an agent.
            * 2nd: The service start time of an agent.
            * 3rd: The departure time of an agent.

        headers : str (optional)
            A comma seperated string of the column headers. Returns
            ``'arrival,service,departure,num_queued,num_total,q_id'``
        
        '''
        qdata = []
        for d in self.data.values():
            qdata.extend(d)
            
        data = np.zeros((len(qdata), 4))
        
        if len(qdata) > 0 :
            data[:] = np.array(qdata)
            dType = [
                ('a_t', float),
                ('ss_t', float),
                ('d_t', float),
                ('q_id', int)
            ]
            data = np.array([tuple(d) for d in data], dtype=dType)
            data = np.sort(data, order='a_t')
            data = np.array([tuple(d) for d in data])                
        if header:
            return data, 'arrival time, service start time, departure time, queue' 
        return data
    
    def schedule_events(self, event_time, event_type, queue):
        heapq.heappush(self.event_queue, (event_time, event_type, queue))
        
    def clock(self): 
        while self.current_time < self.max_clock and self.event_queue:
            event_time, event_type, queue = heapq.heappop(self.event_queue)
            
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
        
        arrival_time = self.current_time
        
        # Schedule next arrival
        next_arrival_time = self.current_time + self.gen_interarrival_time()
        self.schedule_events(next_arrival_time, "Arrival", queue)
        
        customer_id = self.customer_id()
        self.data[customer_id] = [[arrival_time, 0, 0, queue]]
        
        if self.customers_in_system[queue] == 1: #generating departure time
            service_time = self.gen_service_time()
            self.total_time_in_service[queue] += service_time #logging 
            depart_time = self.current_time + service_time
            self.schedule_events(depart_time, "Departure", queue)
            
            self.data[customer_id][-1][1] = self.current_time  # Service start time
            self.data[customer_id][-1][2] = depart_time  # Departure time
        self.customer_movements.append((customer_id, queue))
        

    def handle_departure_event(self, queue):
        self.customers_in_system[queue] -= 1
        self.num_depart += 1
        time_in_system = self.current_time - self.last_event_time #need to work on this
        self.total_time_in_system += time_in_system #logging
        
        if self.customers_in_system[queue] > 0:
            service_time = self.gen_service_time()
            self.total_time_in_service[queue] += service_time
            depart_time = self.current_time + service_time
            self.schedule_events(depart_time, "Departure", queue)
            
            # Find the next customer in queue and update their service start and departure times
            for customer_id, events in self.data.items():
                if events[-1][1] == 0:  # This customer hasn't started service yet
                    events[-1][1] = self.current_time  # Service start time
                    events[-1][2] = depart_time  # Departure time
                    break
        
        next_queue = self.get_next_queue(queue)
        if next_queue is not None:
            self.schedule_events(self.current_time, "Arrival", next_queue)
        
        self.last_event_time = self.current_time
    
    def get_next_queue(self,current_queue):
        probabilities = self.transition_matrix[current_queue]
        next_queue = np.random.choice(len(probabilities), p=probabilities)
        return next_queue if probabilities[next_queue] > 0 else None
        
    def gen_interarrival_time(self):
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
        #theoretical_values = self.calculate_theoretical_values()
        
        print('Simulation results:')
        print(f'Average number of customers in system: {avg_num_in_system:.2f}')
        print(f'Average time spent in system: {avg_time_in_system:.2f}')
        print(f'Average time spent in queue: {avg_time_in_queue:.2f}')
        print(f'Average time spent in service: {avg_time_in_service:.2f}')
        print(f'Average number of customer in queue: {avg_num_in_queue:.2f}')
        #print(self.data)

        # print('\nTheoretical steady-state values:')
        # for i, (L, L_q, W, W_q) in enumerate(theoretical_values):
        #     print(f'Queue {i}:')
        #     print(f'  Average number of customers in system: {L:.2f}')
        #     print(f'  Average number waiting in queue: {L_q:.2f}')
        #     print(f'  Average time spent in system: {W:.2f}')
        #     print(f'  Average time spent in queue: {W_q:.2f}')
    
    # def calculate_theoretical_values(self):
    #     lambdas = np.zeros(len(self.transition_matrix))
    #     lambdas[0] = self.arrival_rate  # Assuming arrivals only happen at the first queue
        
    #     for _ in range(1000):  # Iterate to stabilize arrival rates
    #         lambdas = self.arrival_rate + np.dot(lambdas, self.transition_matrix)
        
    #     theoretical_values = []
    #     for i in range(len(self.transition_matrix)):
    #         lambda_i = lambdas[i]
    #         mu_i = self.service_rate
    #         rho_i = lambda_i / mu_i
            
    #         L_i = rho_i / (1 - rho_i)
    #         W_i = 1 / (mu_i - lambda_i)
    #         L_q_i = (rho_i ** 2) / (1 - rho_i)
    #         W_q_i = lambda_i / (mu_i * (mu_i - lambda_i))
            
    #         theoretical_values.append((L_i, L_q_i, W_i, W_q_i))
        
    #     return theoretical_values
    
    def visualize_customer_movement(self):
        # Create an empty directed graph
        G = nx.DiGraph()

        # Add nodes for each queue
        for i in range(len(self.transition_matrix)):
            G.add_node(i, pos=(i, 0))

        # Add edges based on transition probabilities
        for i in range(len(self.transition_matrix)):
            for j in range(len(self.transition_matrix[i])):
                if self.transition_matrix[i][j] > 0:
                    G.add_edge(i, j)

        # Add edges based on customer movements
        for customer_id, queue in self.customer_movements:
            if len(self.data[customer_id]) > 1:  # Ensure customer moved to another queue
                events = self.data[customer_id]
                for i in range(len(events) - 1):
                    _, _, _ = events[i]  # Extract arrival, service start, and departure times
                    next_arrival_time, _, _ = events[i + 1]
                    G.add_edge(queue, next_arrival_time)

        # Draw the graph
        pos = nx.get_node_attributes(G, 'pos')
        nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000)
        plt.title('Customer Movement Between Queues')
        plt.show()

if __name__ == "__main__":
    transition_matrix = [
        [0.2, 0.4, 0.4],
        [0.1, 0.4, 0.5],
        [0.6, 0.3, 0.1]
    ]
    s = DESsim(10, 15, 20, transition_matrix)
    s.clock()
    s.visualize_customer_movement()
    print(f"customer in system: {s.customers_in_system}, arrival : {s.num_arrivals}, departure: {s.num_depart}, size: {len(s.fetch_data())}")
