import numpy as np
import heapq
import matplotlib.pyplot as plt

class Agent:
    def __init__(self, arrival_time, agent_id):
        self.arrival_time = arrival_time
        self.service_start_time = None
        self.departure_time = None
        self.queue_length_on_arrival = None
        self.server_id = None
        self.agent_id = agent_id  # Unique identifier for the agent

    def __lt__(self, other):
        return self.arrival_time < other.arrival_time

class Server:
    def __init__(self, server_id):
        self.server_id = server_id
        self.is_busy = False
        self.current_agent = None

class Queue:
    def __init__(self, queue_id, num_servers, service_rate):
        self.queue_id = queue_id
        self.servers = [Server(i) for i in range(num_servers)]
        self.service_rate = service_rate
        self.queue = []  # Queue of agents waiting to be served

    def generate_service_time(self):
        # Generate service time using exponential distribution
        return np.random.exponential(1.0 / self.service_rate)

class ClosedQueueNetwork:
    def __init__(self, arrival_rate, service_rates, max_time, num_servers, prob_matrix):
        self.arrival_rate = arrival_rate
        self.service_rates = service_rates
        self.max_time = max_time
        self.num_servers = num_servers
        self.prob_matrix = prob_matrix
        self.queues = [Queue(i, num_servers[i], service_rates[i]) for i in range(len(num_servers))]
        self.time = 0  # Current simulation time
        self.event_queue = []  # Priority queue for managing events
        self.agents_data = []  # List to store data about each agent
        self.agent_counter = 0  # Counter for generating unique agent IDs
    
    def generate_interarrival_time(self):
        # Generate interarrival time using exponential distribution
        return np.random.exponential(1.0 / self.arrival_rate)
    
    def advance_time(self):
        # Advance the simulation time by processing the next event
        if self.event_queue:
            self.time, event_type, agent, queue_id = heapq.heappop(self.event_queue)
            if self.time > self.max_time:
                return False, None, None, None
            return True, event_type, agent, queue_id
        return False, None, None, None
    
    def handle_arrival(self, agent, queue_id):
        # Handle the arrival of an agent at a specific queue
        queue = self.queues[queue_id]
        agent.queue_length_on_arrival = len(queue.queue)
        free_server = next((server for server in queue.servers if not server.is_busy), None)
        if free_server:
            # Assign the agent to the free server
            free_server.is_busy = True
            free_server.current_agent = agent
            agent.service_start_time = self.time
            agent.server_id = free_server.server_id
            service_time = queue.generate_service_time()
            agent.departure_time = self.time + service_time
            heapq.heappush(self.event_queue, (agent.departure_time, 'departure', agent, queue_id))
        else:
            # All servers are busy, so the agent joins the queue
            queue.queue.append(agent)
    
    def handle_departure(self, agent, queue_id):
        # Handle the departure of an agent from a specific queue
        queue = self.queues[queue_id]
        self.agents_data.append([
            agent.agent_id,
            queue_id,
            agent.arrival_time,
            agent.service_start_time,
            agent.departure_time,
            agent.queue_length_on_arrival,
            agent.server_id
        ])
        
        server = queue.servers[agent.server_id]
        server.is_busy = False
        server.current_agent = None
        
        if queue.queue:
            # Start service for the next agent in queue
            next_agent = queue.queue.pop(0)
            server.is_busy = True
            server.current_agent = next_agent
            next_agent.service_start_time = self.time
            next_agent.server_id = server.server_id
            service_time = queue.generate_service_time()
            next_agent.departure_time = self.time + service_time
            heapq.heappush(self.event_queue, (next_agent.departure_time, 'departure', next_agent, queue_id))
        
        # Determine the next queue for the agent based on the probability matrix
        next_queue_id = self.next_queue(queue_id)
        if next_queue_id is not None:
            next_arrival_time = self.time
            agent.arrival_time = next_arrival_time
            heapq.heappush(self.event_queue, (next_arrival_time, 'arrival', agent, next_queue_id))
    
    def next_queue(self, current_queue_id):
        # Determine the next queue based on the probability matrix
        probabilities = self.prob_matrix[current_queue_id]
        next_queue_id = np.random.choice(len(probabilities), p=probabilities)
        return next_queue_id
    
    def simulate(self):
        # Schedule the first arrival
        arrival_time = self.generate_interarrival_time()
        self.agent_counter += 1 # I think I need to move this up
        agent = Agent(arrival_time, self.agent_counter)

        initial_queue_id = 0  # Assuming the first agent starts at queue 0
        heapq.heappush(self.event_queue, (arrival_time, 'arrival', agent, initial_queue_id))
        
        while True:
            continue_simulation, event_type, agent, queue_id = self.advance_time()
            if not continue_simulation:
                break
            
            if event_type == 'arrival':
                self.handle_arrival(agent, queue_id)
            elif event_type == 'departure':
                self.handle_departure(agent, queue_id)

        return np.array(self.agents_data)

    def visualize(self):
        # Convert data to a numpy array for easier handling
        data = np.array(self.agents_data)
        agent_ids = data[:, 0]
        queue_ids = data[:, 1]
        arrival_times = data[:, 2]
        departure_times = data[:, 4]
        queue_lengths = data[:, 5]
        
        plt.figure(figsize=(12, 6))
        for queue_id in np.unique(queue_ids):
            queue_data = data[data[:, 1] == queue_id]
            plt.plot(queue_data[:, 2], queue_data[:, 5], drawstyle='steps-post', label=f'Queue {queue_id}')
        
        plt.xlabel('Time')
        plt.ylabel('Queue Length')
        plt.title('Queue Length Over Time for Different Queues')
        plt.legend()
        plt.grid(True)
        plt.show()

# Example
if __name__ == "__main__":
    arrival_rate = 10  # Lambda (average 2 arrivals per time unit)
    service_rates = [3, 4, 5]  # Mu for each queue (average service rates)
    max_time = 20  # Maximum simulation time
    num_servers = [1, 1, 1]  # Number of servers for each queue

    prob_matrix = [
        [0.0, 0.5, 0.5],  # Probabilities for transitions from queue 0
        [0.2, 0.0, 0.8],  # Probabilities for transitions from queue 1
        [0.3, 0.3, 0.4]   # Probabilities for transitions from queue 2
    ]

    network = ClosedQueueNetwork(arrival_rate, service_rates, max_time, num_servers, prob_matrix)
    agents_data = network.simulate()
    
    #np.save('Data_from_agent', agents_data)
    
    # Print data for each agent
    for data in agents_data:
        print(data)

    # Visualize queue length over time
    network.visualize()
