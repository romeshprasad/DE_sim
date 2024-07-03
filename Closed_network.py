import numpy as np
import matplotlib.pyplot as plt
import heapq

class Agent:
    def __init__(self, agent_id):
        self.arrival_time = 0
        self.service_start_time = None
        self.departure_time = None
        self.queue_length_on_arrival = None
        self.server_id = None
        self.agent_id = agent_id
        self.cycles_completed = 0

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
        self.queue = []

    def generate_service_time(self):
        return round(np.random.exponential(1.0 / self.service_rate), 3)

class OpenQueueNetwork:
    def __init__(self, num_agents, service_rates, max_time, num_servers, prob_matrix, cycle_delay):
        self.num_agents = num_agents
        self.service_rates = service_rates
        self.max_time = max_time
        self.num_servers = num_servers
        self.prob_matrix = prob_matrix
        self.cycle_delay = cycle_delay
        self.queues = [Queue(i, num_servers[i], service_rates[i]) for i in range(len(num_servers))]
        self.time = 0
        self.event_queue = []
        self.agents_data = []
        self.agent_counter = 0
        self.master_queue = [(0, "source", "target", "event_type")]
        self.agents = [Agent(i) for i in range(num_agents)]
    
    def advance_time(self):
        if self.event_queue:
            self.time, event_type, agent, queue_id = heapq.heappop(self.event_queue)
            if self.time > self.max_time:
                return False, None, None, None
            return True, event_type, agent, queue_id
        return False, None, None, None
    
    def handle_arrival(self, agent, queue_id):
        queue = self.queues[queue_id]
        agent.queue_length_on_arrival = len(queue.queue)
        free_server = next((server for server in queue.servers if not server.is_busy), None)
        
        if free_server:
            self.assign_server(free_server, agent, queue_id)
        else:
            queue.queue.append(agent)
        
        self.capture_event(agent, queue_id, 'arrival')
    
    def handle_departure(self, agent, queue_id):
        queue = self.queues[queue_id]
        self.log_departure(agent, queue_id)
        server = queue.servers[agent.server_id]
        server.is_busy = False
        server.current_agent = None
        
        if queue.queue:
            next_agent = queue.queue.pop(0)
            self.assign_server(server, next_agent, queue_id)
        
        next_queue_id = self.next_queue(queue_id)
        if next_queue_id is not None:
            agent.arrival_time = self.time
            agent.server_id = None
            heapq.heappush(self.event_queue, (self.time, 'arrival', agent, next_queue_id))
        
        self.capture_event(agent, queue_id, 'departure')
        self.schedule_reentry(agent)  # Reintroduce the agent into the system
    
    def assign_server(self, server, agent, queue_id):
        server.is_busy = True
        server.current_agent = agent
        agent.service_start_time = self.time
        agent.server_id = server.server_id
        service_time = self.queues[queue_id].generate_service_time()
        agent.departure_time = self.time + service_time
        heapq.heappush(self.event_queue, (agent.departure_time, 'departure', agent, queue_id))
    
    def log_departure(self, agent, queue_id):
        self.agents_data.append([
            agent.agent_id,
            agent.arrival_time,
            agent.service_start_time,
            agent.departure_time,
            agent.server_id,
            queue_id,
            agent.queue_length_on_arrival,
            agent.cycles_completed
        ])
    
    def next_queue(self, current_queue_id):
        probabilities = self.prob_matrix[current_queue_id]
        next_queue_id = np.random.choice(len(probabilities), p=probabilities)
        return next_queue_id if next_queue_id != len(probabilities) else None
    
    def capture_event(self, agent, queue_id, event_type):
        pass
        # Nodes = self.get_node()
        # server_id = agent.server_id if agent.server_id is not None else 0
        # if queue_id == 0 and event_type == 'arrival':
        #     source = Nodes[0]
        #     target = Nodes[self.get_index_from_list(server_id, queue_id, self.num_servers)]
        # elif event_type == 'departure' and queue_id == len(self.num_servers) - 1:
        #     source = Nodes[self.get_index_from_list(server_id, queue_id, self.num_servers)]
        #     target = Nodes[-1]
        # else:
        #     source = Nodes[self.get_index_from_list(server_id, queue_id, self.num_servers)]
        #     target = Nodes[self.get_index_from_list(server_id, queue_id + 1, self.num_servers)]
        
        # self.master_queue.append([self.time, source, target, event_type])
    
    # def get_node(self):
    #     Nodes = [0]
    #     current_node_index = 1
    #     for stage, num_servers in enumerate(self.num_servers):
    #         for _ in range(num_servers):
    #             Nodes.append(current_node_index)
    #             current_node_index += 1
    #     Nodes.append(current_node_index)
    #     return Nodes
    
    # def get_index_from_list(self, worker_number, stage_number, num_servers):
    #     offset = 1
    #     for stage in range(stage_number):
    #         offset += num_servers[stage]
    #     index = offset + worker_number
    #     total_servers = sum(num_servers)
    #     if index < 1 or index > total_servers:
    #         raise ValueError(f"Invalid index: {index}. Worker number: {worker_number}, Stage number: {stage_number}")
    #     return index
    
    def schedule_reentry(self, agent):
        agent.cycles_completed += 1
        reentry_time = self.time + self.cycle_delay
        agent.arrival_time = reentry_time
        heapq.heappush(self.event_queue, (reentry_time, 'arrival', agent, 0))

    
    def simulate(self):
        for agent in self.agents:
            heapq.heappush(self.event_queue, (agent.arrival_time, 'arrival', agent, 0))
        
        while True:
            continue_simulation, event_type, agent, queue_id = self.advance_time()
            if not continue_simulation:
                break
            
            if event_type == 'arrival':
                self.handle_arrival(agent, queue_id)
            elif event_type == 'departure':
                self.handle_departure(agent, queue_id)
                              
        return np.array(self.agents_data), np.array(self.master_queue)

    def visualize(self):
        data = np.array(self.agents_data)
        plt.figure(figsize=(12, 6))
        for queue_id in np.unique(data[:, 5]):
            queue_data = data[data[:, 5] == queue_id]
            plt.plot(queue_data[:, 1], queue_data[:, 6], drawstyle='steps-post', label=f'Queue {queue_id}')
        
        plt.xlabel('Time')
        plt.ylabel('Queue Length')
        plt.title('Queue Length Over Time for Different Queues')
        plt.legend()
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    num_agents = 5
    service_rates = [1, 1.5]
    max_time = 10
    num_servers = [1, 2]
    prob_matrix = [[0.5, 0.5], [0.3, 0.7]]
    cycle_delay = 1.0

    np.random.seed(2)
    network = OpenQueueNetwork(num_agents, service_rates, max_time, num_servers, prob_matrix, cycle_delay)
    agents_data, master_queue = network.simulate()   
    
    print(agents_data, master_queue)
    # network.visualize()
