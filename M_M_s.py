import numpy as np
import heapq
import math
import matplotlib.pyplot as plt

class Agent:
    def __init__(self, arrival_time, agent_id):
        self.arrival_time = arrival_time
        self.service_start_time = None
        self.departure_time = None
        self.queue_length_on_arrival = None
        self.server_id = None
        self.agent_id = agent_id

    def __lt__(self, other):
        return self.arrival_time < other.arrival_time

class Server:
    def __init__(self, server_id):
        self.server_id = server_id
        self.is_busy = False
        self.current_agent = None

class MMmQueue:
    def __init__(self, arrival_rate, service_rate, max_time, num_servers):
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.max_time = max_time
        self.num_servers = num_servers
        self.queue = []  # Queue of agents waiting to be served
        self.time = 0  # Current simulation time
        self.event_queue = []  # Priority queue for managing events
        self.agents_data = []  # List to store data about each agent
        self.servers = [Server(i) for i in range(num_servers)]  # List of servers
        self.agent_counter = 0
        
        
        
        self.master_queue = [(0, "Source", "Target", "l_queue")]
        self.arrival = 0 # this are number for data logging
        self.departure = num_servers + 1 

        
        #simulation logging 
        self.total_time_in_system = 0
        self.total_customers = 0
        self.total_time_in_service = 0
    
    def generate_interarrival_time(self):
        # Generate interarrival time using exponential distribution
        return round(np.random.exponential(1.0 / self.arrival_rate),3)
    
    def generate_service_time(self):
        # Generate service time using exponential distribution
        return round(np.random.exponential(1.0 / self.service_rate),3)
    
    def advance_time(self):
        # Advance the simulation time by processing the next event
        if self.event_queue:
            self.time, event_type, agent = heapq.heappop(self.event_queue)
            if self.time > self.max_time:
                return False, None, None
            return True, event_type, agent
        return False, None, None
    
    def handle_arrival(self, agent):
        # Handle the arrival of an agent
        agent.queue_length_on_arrival = len(self.queue)
        free_server = next((server for server in self.servers if not server.is_busy), None)
        if free_server:
            # Assign the agent to the free server
            free_server.is_busy = True
            free_server.current_agent = agent
            agent.service_start_time = self.time
            agent.server_id = free_server.server_id
            service_time = self.generate_service_time()
            agent.departure_time = self.time + service_time
            heapq.heappush(self.event_queue, (agent.departure_time, 'departure', agent))
        else:
            # All servers are busy, so the agent joins the queue
            self.queue.append(agent)
        
        # Schedule the next arrival if within max_time
        next_arrival_time = self.time + self.generate_interarrival_time()
        if next_arrival_time <= self.max_time:
            self.agent_counter += 1
            next_agent = Agent(next_arrival_time, self.agent_counter)
            heapq.heappush(self.event_queue, (next_arrival_time, 'arrival', next_agent))
    
    def handle_departure(self, agent):
        # Handle the departure of an agent
        self.agents_data.append([
            agent.arrival_time,
            agent.service_start_time,
            agent.departure_time,
            agent.queue_length_on_arrival,
            agent.server_id,
            agent.agent_id
        ])
        
        server = self.servers[agent.server_id]
        server.is_busy = False
        server.current_agent = None
        
        if self.queue:
            # Start service for the next agent in queue
            next_agent = self.queue.pop(0)
            server.is_busy = True
            server.current_agent = next_agent
            next_agent.service_start_time = self.time
            next_agent.server_id = server.server_id
            service_time = self.generate_service_time()
            next_agent.departure_time = self.time + service_time
            heapq.heappush(self.event_queue, (next_agent.departure_time, 'departure', next_agent))
    
    def simulate(self):
        # Schedule the first arrival
        arrival_time = self.generate_interarrival_time()
        self.agent_counter += 1
        agent = Agent(arrival_time, self.agent_counter)
        heapq.heappush(self.event_queue, (arrival_time, 'arrival', agent))
        
        while True:
            continue_simulation, event_type, agent = self.advance_time()
            if not continue_simulation:
                break
            
            if event_type == 'arrival':
                self.handle_arrival(agent)
                if agent.server_id == None:
                    server_id = 1
                    self.master_queue.append([self.time, self.arrival, server_id, agent.queue_length_on_arrival])
                else:
                    self.master_queue.append([self.time, self.arrival, agent.server_id + 1, agent.queue_length_on_arrival])
            elif event_type == 'departure':
                self.handle_departure(agent)
                self.master_queue.append([self.time, agent.server_id + 1, self.departure, 0])
            
            #self.master_queue.append([self.time, event_type,  agent.server_id])

        return np.array(self.agents_data), np.array(self.master_queue)
    
    def logging(self):
        
        #hande data as numpy array
        data = np.array(self.agents_data)
        departure_time = data[:,2]
        arrival_time = data[:,0]
        service_start_time = data[:,1]
        queue_length = data[:,3]
        total_time_in_system = sum(departure_time) - sum(arrival_time)
        total_time_in_service = sum(departure_time) - sum(service_start_time)
        total_customers = max(data[:,5])
        
        #simulation results
        avg_num_in_system = total_time_in_system / self.time if self.time > 0 else 0
        avg_num_in_queue = sum(queue_length)/total_customers
        avg_time_in_system = total_time_in_system / total_customers if total_customers > 0 else 0
        avg_time_in_service = total_time_in_service / total_customers if total_customers > 0 else 0
        avg_time_in_queue = avg_time_in_system - avg_time_in_service
        
        print('Simulation results:')
        print(f'Average number of customers in system: {avg_num_in_system:.2f}')
        print(f'Average number of customers in queue: {avg_num_in_queue:.2f}')
        print(f'Average time spent in system: {avg_time_in_system:.2f}')
        print(f'Average time spent in queue: {avg_time_in_queue:.2f}')
        print(f'Average time spent in service: {avg_time_in_service:.2f}')
        
        #theoretical results    
        rho = self.arrival_rate / (num_servers*self.service_rate)
        A = 0
        for a in range(0, num_servers):
            A += pow((num_servers*rho), a) / math.factorial(a)
        B = pow((num_servers * rho), num_servers) / (math.factorial(num_servers)*(1-rho)) 
        pi_0 = 1 /  (A + B)
        
        p_custo_gth_service_num = pow((num_servers*rho),num_servers)* pi_0
        p_custo_gth_service_den = (math.factorial(num_servers))*(1-rho)
        p_cust_gth_ser = p_custo_gth_service_num / p_custo_gth_service_den
        
        L_q = p_cust_gth_ser * rho / (1 - rho)
        W_q = L_q / arrival_rate
        L = L_q +  (arrival_rate/service_rate)
        W = L / arrival_rate
        
        print('\nTheoretical steady-state values:')
        print(f'Steady state: {pi_0}, rho: {rho}, P(cust>server) : {p_cust_gth_ser}')
        print(f'Average number of customers in system: {L:.2f}')
        print(f'Average number in queue: {L_q:.2f}')
        print(f'Average time spent in system: {W:.2f}')
        print(f'Average time spent in queue: {W_q:.2f}')
        print(f'Average time spent in service: {1 / self.service_rate:.2f}')                   

    def visualize(self):
        # Convert data to a numpy array for easier handling
        data = np.array(self.agents_data)
        
        # Extract unique server IDs
        server_ids = np.unique(data[:, 4])

        # Initialize dictionaries to store arrival rates and queue lengths for each server
        arrival_rates = {server_id: [] for server_id in server_ids}
        queue_lengths = {server_id: [] for server_id in server_ids}

        # Populate the dictionaries with data
        for entry in data:
            server_id = entry[4]
            arrival_rate = entry[0]
            queue_length = entry[3]
            arrival_rates[server_id].append(arrival_rate)
            queue_lengths[server_id].append(queue_length)

        # Plot the data
        plt.figure(figsize=(12, 6))

        for server_id in server_ids:
            plt.plot(arrival_rates[server_id], queue_lengths[server_id], drawstyle='steps-post', label=f'q_server_{int(server_id)}')

        plt.xlabel('Time')
        plt.ylabel('Queue Length')
        plt.title('Queue Length Over Time')
        plt.grid(True)
        plt.legend()
        plt.show()

# Example usage
if __name__ == "__main__":
    arrival_rate = 10  # Lambda 
    service_rate = 15  # Mu 
    max_time = 10  # Maximum simulation time
    num_servers = 5  # Number of servers

    mm_m_queue = MMmQueue(arrival_rate, service_rate, max_time, num_servers)
    agents_data, master_queue = mm_m_queue.simulate()
    
    print(master_queue)
    
    # Print data for each agent
    for data in agents_data:
        print(data)
        
    #mm_m_queue.logging()

    # Visualize queue length over time
    #mm_m_queue.visualize()
    
    np.save("Data from 5 server", master_queue)
