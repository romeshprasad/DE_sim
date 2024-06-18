import numpy as np
import heapq
import matplotlib.pyplot as plt

class Agent:
    def __init__(self, arrival_time):
        self.arrival_time = arrival_time
        self.service_start_time = None
        self.departure_time = None
        self.queue_length_on_arrival = None
        self.server_id = None

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
    
    def generate_interarrival_time(self):
        # Generate interarrival time using exponential distribution
        return np.random.exponential(1.0 / self.arrival_rate)
    
    def generate_service_time(self):
        # Generate service time using exponential distribution
        return np.random.exponential(1.0 / self.service_rate)
    
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
            next_agent = Agent(next_arrival_time)
            heapq.heappush(self.event_queue, (next_arrival_time, 'arrival', next_agent))
    
    def handle_departure(self, agent):
        # Handle the departure of an agent
        self.agents_data.append([
            agent.arrival_time,
            agent.service_start_time,
            agent.departure_time,
            agent.queue_length_on_arrival,
            agent.server_id
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
        agent = Agent(arrival_time)
        heapq.heappush(self.event_queue, (arrival_time, 'arrival', agent))
        
        while True:
            continue_simulation, event_type, agent = self.advance_time()
            if not continue_simulation:
                break
            
            if event_type == 'arrival':
                self.handle_arrival(agent)
            elif event_type == 'departure':
                self.handle_departure(agent)

        return np.array(self.agents_data)

    def visualize(self):
        # Convert data to a numpy array for easier handling
        data = np.array(self.agents_data)
        arrival_times = data[:, 0]
        departure_times = data[:, 2]
        queue_lengths = data[:, 3]
        
        plt.figure(figsize=(12, 6))
        plt.plot(arrival_times, queue_lengths, drawstyle='steps-post')
        plt.xlabel('Time')
        plt.ylabel('Queue Length')
        plt.title('Queue Length Over Time')
        plt.grid(True)
        plt.show()

# Example usage
if __name__ == "__main__":
    arrival_rate = 3  # Lambda (average 2 arrivals per time unit)
    service_rate = 4  # Mu (average 3 services per time unit)
    max_time = 10  # Maximum simulation time
    num_servers = 2  # Number of servers

    mm_m_queue = MMmQueue(arrival_rate, service_rate, max_time, num_servers)
    agents_data = mm_m_queue.simulate()
    
    # Print data for each agent
    for data in agents_data:
        print(data)

    # Visualize queue length over time
    mm_m_queue.visualize()
