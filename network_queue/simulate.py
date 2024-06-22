from openqueue import OpenQueueNetwork   
from agent import Agent
import heapq 
import numpy as np
from master_queue import fetch_data
    
class simulator():
    def __init__(self, arrival_rate, service_rates, max_time, num_servers, prob_matrix):
        self.network = OpenQueueNetwork(arrival_rate, service_rates, max_time, num_servers, prob_matrix)
 
    def simulate(self):
        # Schedule the first arrival
        arrival_time = self.network.generate_interarrival_time()

        self.network.agent_counter += 1   # Generate a unique ID for each agent
        agent = Agent(arrival_time, self.network.agent_counter)

        initial_queue_id = 0  # Assuming the first agent starts at queue 0 #need to change this to stage_id
        heapq.heappush(self.network.event_queue, (arrival_time, 'arrival', agent, initial_queue_id))
        
        while True:
            continue_simulation, event_type, agent, queue_id = self.network.advance_time()
            if not continue_simulation:
                break
            
            if event_type == 'arrival':
                self.network.handle_arrival(agent, queue_id)
            elif event_type == 'departure':
                self.network.handle_departure(agent, queue_id)
        
        return np.array(self.network.agents_data), np.array(self.network.master_queue)