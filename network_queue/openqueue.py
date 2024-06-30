import numpy as np
from Queue_and_service import Queue
from agent import Agent
import heapq
from master_queue import fetch_data

class OpenQueueNetwork:
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
        self.master_queue = [(0, "source", "target", "event_type")]
        self.arrival = 0
        self.departure = sum(num_servers) + 1
     
    def generate_interarrival_time(self):
        # Generate interarrival time using exponential distribution
        return round(np.random.exponential(1.0 / self.arrival_rate),3)
    
    def advance_time(self):
        # Advance the simulation time by processing the next event
        if self.event_queue:
            self.time, event_type, agent, queue_id = heapq.heappop(self.event_queue)
            if self.time > self.max_time:
                return False, None, None, None
            return True, event_type, agent, queue_id
        return False, None, None, None
    
    def handle_arrival(self, agent, queue_id): #
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
    
            #schedule next arrival if it's in the initial queue
        if queue_id == 0:  # Only schedule new arrivals if it's the initial queue
            next_arrival_time = self.time + self.generate_interarrival_time()
            self.agent_counter += 1
            new_agent = Agent(next_arrival_time, self.agent_counter)
            heapq.heappush(self.event_queue, (next_arrival_time, 'arrival', new_agent, 0))
            
        print(f"Arrival - Time: {self.time}, Agent ID: {agent.agent_id}, Assigned Server: {agent.server_id}, Queue ID: {queue_id}")
        
        
        # Capture the arrival event
        Nodes = self.get_node()
        server_id = agent.server_id if agent.server_id is not None else 0
        if queue_id == 0:
            source = Nodes[0]  # Arrival node
            target = Nodes[self.get_index_from_list(server_id, queue_id, self.num_servers)]
        else:
            source = Nodes[self.get_index_from_list(server_id, queue_id - 1, self.num_servers)]
            target = Nodes[self.get_index_from_list(server_id, queue_id, self.num_servers)]
            
        self.master_queue.append([self.time, source, target, 'arrival'])
        
        print(f"Arrival - Time: {self.time}, Agent ID: {agent.agent_id}, Source: {source}, target: {target}, Queue ID: {queue_id}")
    
    def handle_departure(self, agent, queue_id):
        # Handle the departure of an agent from a specific queue
        queue = self.queues[queue_id]
        
        #Log the departure
        self.agents_data.append([
            agent.agent_id,
            agent.arrival_time,
            agent.service_start_time,
            agent.departure_time,
            agent.server_id,
            queue_id,
            agent.queue_length_on_arrival
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
        if queue_id != len(self.prob_matrix) - 1:
            next_queue_id = self.next_queue(queue_id)
            if next_queue_id is not None:
                next_arrival_time = self.time
                agent.arrival_time = next_arrival_time
                # Remap the server ID if moving to a different stage
                if next_queue_id != queue_id:
                    agent.server_id = None  # Reset the server ID as it will be reassigned in the next stage
                heapq.heappush(self.event_queue, (next_arrival_time, 'arrival', agent, next_queue_id))
        
        print(f"Departure - Time: {self.time}, Agent ID: {agent.agent_id}, Released Server: {agent.server_id}, Queue ID: {queue_id}")
          
        Nodes = self.get_node()
        server_id = agent.server_id if agent.server_id is not None else 0
        if queue_id == len(self.num_servers) - 1:
            source = Nodes[self.get_index_from_list(server_id, queue_id, self.num_servers)]
            target = Nodes[-1]  # Departure node
            
        else:
            source = Nodes[self.get_index_from_list(server_id, queue_id, self.num_servers)]
            target = Nodes[self.get_index_from_list(server_id, queue_id + 1, self.num_servers)]
        
        print(f"Departure - Time: {self.time}, Agent ID: {agent.agent_id}, Source: {source}, target: {target}, Queue ID: {queue_id}")  
        
        self.master_queue.append([self.time, source, target, 'departure'])
    
    def next_queue(self, current_queue_id):
        # Determine the next queue based on the probability matrix
        probabilities = self.prob_matrix[current_queue_id]
        next_queue_id = np.random.choice(len(probabilities), p=probabilities)
        return next_queue_id if next_queue_id != len(probabilities) else None
    
    #function used for graph plotting
    def get_node(self):
        # Generate nodes and their positions
        Nodes = [0]  # Start with the arrival node
        pos = {0: (0, 0)}
        current_node_index = 1

        # Generate nodes and positions for each stage
        for stage, num_servers in enumerate(self.num_servers):
            for server in range(num_servers):
                Nodes.append(current_node_index)
                #pos[current_node_index] = (stage + 1, server)
                current_node_index += 1
        # Add departure node
        Nodes.append(current_node_index)
        return Nodes
    
    def get_index_from_list(self, worker_number, stage_number, num_servers):
    # Initialize the offset for the current stage
        offset = 1  # Start from 1 because 0 is reserved for arrival
        
        # Calculate the offset by summing the number of servers in previous stages
        for stage in range(stage_number):
            offset += num_servers[stage]
        
        # The index in the list is the offset plus the worker number
        index = offset + worker_number
        print(f"Worker number: {worker_number}, Stage number: {stage_number}")
        total_servers = sum(num_servers)
        if index < 1 or index > total_servers:
            raise ValueError(f"Invalid index: {index}. Worker number: {worker_number}, Stage number: {stage_number}")
        
        return index