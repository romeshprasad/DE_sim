import numpy as np
import heapq
import matplotlib.pyplot as plt

class Agent:
    def __init__(self, arrival_time, agent_id):
        self.agent_id = agent_id
        self.arrival_time = arrival_time
        self.service_start_time = None
        self.service_end_time = None
        self.server_id = None
        self.queue_length_on_arrival = None

class Server:
    def __init__(self, server_id):
        self.server_id = server_id
        self.is_busy = False

class Queue:
    def __init__(self, queue_id, num_servers, service_rate, capacity=float('inf')):
        self.queue_id = queue_id
        self.servers = [Server(i) for i in range(num_servers)]
        self.service_rate = service_rate
        self.queue = []  # Queue of agents waiting to be served
        self.capacity = capacity  # Maximum capacity of the queue

class OpenQueueNetwork:
    def __init__(self, arrival_rate, service_rates, max_time, num_servers, prob_matrix, capacities=None):
        self.arrival_rate = arrival_rate
        self.service_rates = service_rates
        self.time = 0 
        self.max_time = max_time
        self.num_servers = num_servers
        self.prob_matrix = prob_matrix
        self.queues = [Queue(i, num_servers[i], service_rates[i], capacities[i] if capacities else float('inf')) for i in range(len(num_servers))]
        self.event_queue = []  
        self.agents_data = [] 
        self.agent_counter = 0
        self.rejected_agents = []  # List to store rejected agents
        self.arrival = 0
        self.departure = sum(num_servers) + 1
        self.agents = Agent(self.time, self.agent_counter)  # Initialize agent

    def schedule_next_arrival(self):
        inter_arrival_time = np.random.exponential(1 / self.arrival_rate)
        next_arrival_time = self.time + inter_arrival_time
        if next_arrival_time <= self.max_time:
            heapq.heappush(self.event_queue, (next_arrival_time, self.arrival, self.agent_counter))
            self.agent_counter += 1

    def handle_arrival(self, agent, queue_id):
        queue = self.queues[queue_id]
        agent.queue_length_on_arrival = len(queue.queue)
        free_server = next((server for server in queue.servers if not server.is_busy), None)
        
        if free_server:
            # Assign the agent to the free server
            self.assign_server(free_server, agent, queue_id)
        else:
            # Check if the queue has reached its capacity
            if len(queue.queue) < queue.capacity:
                # All servers are busy, so the agent joins the queue
                queue.queue.append(agent)
            else:
                print(f"Queue {queue_id} is full. Agent {agent.agent_id} is rejected.")
                # Optionally handle the rejected agent (e.g., log it or count it)
                self.rejected_agents.append(agent)
        
        # Schedule next arrival if it's in the initial queue
        if queue_id == 0:
            self.schedule_next_arrival()
            
        print(f"Arrival - Time: {self.time}, Agent ID: {agent.agent_id}, Assigned Server: {agent.server_id}, Queue ID: {queue_id}")

    def handle_departure(self, agent, queue_id):
        queue = self.queues[queue_id]
        server = queue.servers[agent.server_id]
        server.is_busy = False
        
        if queue.queue:
            # Serve the next agent in the queue
            next_agent = queue.queue.pop(0)
            self.assign_server(server, next_agent, queue_id)
        
        # Move agent to the next queue if applicable
        next_queue_id = np.random.choice(range(len(self.prob_matrix[queue_id])), p=self.prob_matrix[queue_id])
        if next_queue_id != queue_id:
            self.handle_arrival(agent, next_queue_id)
        
        print(f"Departure - Time: {self.time}, Agent ID: {agent.agent_id}, Server ID: {agent.server_id}, Queue ID: {queue_id}")

    def assign_server(self, server, agent, queue_id):
        server.is_busy = True
        agent.service_start_time = self.time
        service_time = np.random.exponential(1 / self.service_rates[queue_id])
        agent.service_end_time = self.time + service_time
        agent.server_id = server.server_id
        heapq.heappush(self.event_queue, (agent.service_end_time, self.departure, agent.agent_id))

    def simulate(self):
        self.schedule_next_arrival()
        
        while self.event_queue and self.time <= self.max_time:
            self.time, event_type, agent_id = heapq.heappop(self.event_queue)
            
            if event_type == self.arrival:
                agent = Agent(self.time, agent_id)
                self.agents_data.append(agent)
                self.handle_arrival(agent, 0)
            elif event_type == self.departure:
                agent = next(agent for agent in self.agents_data if agent.agent_id == agent_id)
                queue_id = next(queue.queue_id for queue in self.queues if any(server.server_id == agent.server_id for server in queue.servers))
                self.handle_departure(agent, queue_id)
        
        return self.agents_data

    def visualize(self):
        # Convert data to a numpy array for easier handling
        data = np.array(self.agents_data)
        agent_ids = data[:, 0]
        arrival_times = data[:, 1]
        service_start_times = data[:, 2]
        departure_times = data[:, 3]
        server_ids = data[:, 4]
        queue_ids = data[:, 5]
        queue_lengths = data[:, 6]
        
        plt.figure(figsize=(12, 6))
        for queue_id in np.unique(queue_ids):
            queue_data = data[data[:, 5] == queue_id]
            plt.plot(queue_data[:, 1], queue_data[:, 6], drawstyle='steps-post', label=f'Queue {queue_id}')
        
        plt.xlabel('Time')
        plt.ylabel('Queue Length')
        plt.title('Queue Length Over Time for Different Queues')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__=="__main__":
    arrival_rate = 1.0
    service_rates = [1, 1.5, 2]
    max_time = 10
    num_servers = [1, 1, 1]
    prob_matrix = [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.0, 0.0]]
    capacities = [5, 10, 15]  # Set capacities for each queue

    np.random.seed(2)
    network = OpenQueueNetwork(arrival_rate, service_rates, max_time, num_servers, prob_matrix, capacities)
    agents_data = network.simulate()
    
    print(agents_data)
    
    np.save("agent_data.npy", agents_data)

    # Visualize the results
    network.visualize()
