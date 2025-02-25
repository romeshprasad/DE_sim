import numpy as np
import heapq
import matplotlib.pyplot as plt

class Agent:
    def __init__(self, arrival_time, agent_id):
        """ 
        The base class for the agent. The agent moves through the network.

        Parameters:
        arrival_time: arrival time of the agent
        agent_id: the unique id of the agent

        Returns:
        It returns attributes of each agent: 
        arrival_time: Time when the agent arrives in the system
        service_start_time: Time when the agent starts it service
        departure_time: Time when the agent departs
        queue_length on arrival: Queue length when the agent arrives in the system
        server_id: The server number which provides service to the agent
        agent_id:  The unique number of the agent  
        """

        self.arrival_time = arrival_time
        self.service_start_time = None
        self.departure_time = None
        self.queue_length_on_arrival = None
        self.server_id = None
        self.agent_id = agent_id
         

    def __lt__(self, other):
        return self.arrival_time < other.arrival_time
    
    def generate_interarrival_time(self, arrival_rate):
        # Generate interarrival time using exponential distribution
        return round(np.random.exponential(1.0 / arrival_rate),3)

class Server:
    """
    Base class for the server. 

    Parameters:
    server_id: Unique id of the server

    Return:
    It returns atributes for each server
    server_id: Unique id for the agent
    is_busy: Boolean
    current_agent: Attribute of the agent that is gettng service
    """
    def __init__(self, server_id):
        self.server_id = server_id
        self.is_busy = False
        self.current_agent = None

class Queue:
    """
    Base class for the queue.

    Parameters:
    queue_id: The current id of the queue
    num_servers: The number of servers
    service_rate: The service rate of the servers

    Returns:
    Attributes of the queue
    servers: A list of the attributes for each server
    queue: empty list- agents that find the server occupied joins the queue
    generate_service_time: A service time for the agent following an exponential distribution 
    """
    
    def __init__(self, queue_id, num_servers, service_rate):
        self.queue_id = queue_id
        self.servers = [Server(i) for i in range(num_servers)]
        self.service_rate = service_rate
        self.queue = []  # Queue of agents waiting to be served

    def generate_service_time(self):
        # Generate service time using exponential distribution
        return round(np.random.exponential(1.0 / self.service_rate),3)


class OpenQueueNetwork:
    """
    A queue simulator that simulates a Jackson network/series queue. 

    Parameter:
    arrival_rate: The interarrival rate of the customer
    service_rate: The service rate for each customer
    max_time: The max simulation time
    num_servers: The number of servers in the system
    prob_matrix: A transition matrix that describes the movement of agents from queue's

    Attributes:
    arrival_rate: int or float
    service_rate: list of service rate for each server. 
    max_time: int or float
    num_servers: list of number of servers for each stage
    prob_matrix: array
    queues: A list of class Queues.
            The length of queues is the length of the num_servers
    time: initialize time
    event_queue: list- queue event handler
    agents_data: list- store data about each agent
    agent_counter: int- counter for generating unique id for the agent
    master_queue: list- used for plotting graph network
    agents: Initialize Agent class  
    """

    def __init__(self, arrival_rate, service_rates, max_time, num_servers, prob_matrix):
        self.arrival_rate = arrival_rate
        self.service_rates = service_rates
        self.time = 0 
        self.max_time = max_time
        self.num_servers = num_servers
        self.prob_matrix = prob_matrix
        self.queues = [Queue(i, num_servers[i], service_rates[i]) for i in range(len(num_servers))]
        self.event_queue = []  
        self.agents_data = [] 
        self.agent_counter = 0

        """
        plotting network queue
        """
        source = 0
        sink = sum(num_servers) + 1
        queue_len = 0  
        #self.master_queue = [(self.time, self.agent_counter, "initialize", source, sink, queue_len)]
        
        #source = 0
        #target = sum(num_servers) + 1
        #self.master_queue = [(source, target)]

        self.arrival = 0
        self.departure = sum(num_servers) + 1
        self.agents = Agent(self.time,self.agent_counter) #initialize agent
    
    def advance_time(self):
        """
        This function advances simulation time by removing the least time from the event_queue list
        Additionally, it ensures the current time does not exceed the maximum simulation time
        """
        if self.event_queue:
            self.time, event_type, agent, queue_id = heapq.heappop(self.event_queue)
            if self.time > self.max_time:
                return False, None, None, None
            return True, event_type, agent, queue_id
        return False, None, None, None
    
    def assign_server(self, server, agent, queue_id):
        """
        This function assign servers to the agent

        Parameter:
        server: list of server
        agent: Agents attributes
        queue_id: current stage of the agent

        Attributes:
        It updates the server status to is busy, starts the service of the agent,
        generates departure time for the agent and push the agent in to the event_queue
        """

        server.is_busy = True
        server.current_agent = agent
        agent.service_start_time = self.time
        agent.server_id = server.server_id
        service_time = self.queues[queue_id].generate_service_time()
        agent.departure_time = self.time + service_time
        heapq.heappush(self.event_queue, (agent.departure_time, 'departure', agent, queue_id))

    def schedule_next_arrival(self):
        """
        Schedules the next arrival
        """

        next_arrival_time = self.time + self.agents.generate_interarrival_time(self.arrival_rate)
        self.agent_counter += 1
        new_agent = Agent(next_arrival_time, self.agent_counter)
        heapq.heappush(self.event_queue, (next_arrival_time, 'arrival', new_agent, 0))
    
    def handle_arrival(self, agent, queue_id):
        """
        Handles the arrival event.
        This function checks if the server is free.
        If the server is free, the agent enters service and departure is scheduled
        Else, the agent joins the queue.

        Also, if it is first queue/stage than we schedule future arrival for the first queue/stage

        Parameter:
        agent: The attributes of the agent from the class Agent
        queue_id: The current stage at which the agent arrives

        """
        # Handle the arrival of an agent at a specific queue
        queue = self.queues[queue_id] 
        agent.queue_length_on_arrival = len(queue.queue)
        free_server = next((server for server in queue.servers if not server.is_busy), None)
        
        if free_server:
            # Assign the agent to the free server
            self.assign_server(free_server, agent, queue_id)  
        else:
            # All servers are busy, so the agent joins the queue
            queue.queue.append(agent)
    
        #schedule next arrival if it's in the initial queue
        if queue_id == 0:
            self.schedule_next_arrival()
            
        print(f"Arrival - Time: {self.time}, Agent ID: {agent.agent_id}, Assigned Server: {agent.server_id}, Queue ID: {queue_id}")
        
    
    def log_departure(self, agent, queue_id):
        """
        log agent's data along with queue_id.
        It is used for statistical calculations
        """
        self.agents_data.append([
            agent.agent_id,
            agent.arrival_time,
            agent.service_start_time,
            agent.departure_time,
            agent.server_id,
            queue_id,
            agent.queue_length_on_arrival
        ])

    def handle_departure(self, agent, queue_id):
        """
        This function handle the departure event.
        If there is a queue then the agent is selected from the queue to serve.
        It also checks if this is the last queue/stage. 
        If it is the last stage then it departs from the system
        Else, the next stage/queue is decided for the queue from the transition probability matrix
        """
        # Handle the departure of an agent from a specific queue
        queue = self.queues[queue_id]
        
        #Log the departure
        self.log_departure(agent, queue_id)
        
        server = queue.servers[agent.server_id]
        server.is_busy = False
        server.current_agent = None
        
        if queue.queue:
            # Start service for the next agent in queue
            next_agent = queue.queue.pop(0)
            self.assign_server(server, next_agent, queue_id)
            
        
        # Determine the next queue for the agent based on the probability matrix
        # check the current q is the last q. If it is then we do not schedule arrival
        if queue_id != len(self.prob_matrix) - 1:
            next_queue_id = self.next_queue(queue_id)
            if next_queue_id is not None:
                next_arrival_time = self.time
                agent.arrival_time = next_arrival_time #+ 1e-2 # add a delay
                # Remap the server ID if moving to a different stage
                if next_queue_id != queue_id:
                    agent.server_id = None  # Reset the server ID as it will be reassigned in the next stage
                heapq.heappush(self.event_queue, (next_arrival_time, 'arrival', agent, next_queue_id))
        
        print(f"Departure - Time: {self.time}, Agent ID: {agent.agent_id}, Released Server: {agent.server_id}, Queue ID: {queue_id}")  
    
    def next_queue(self, current_queue_id):
        """
        Determine the next queue based on the probability matrix given current_queue
        """
        
        probabilities = self.prob_matrix[current_queue_id]
        next_queue_id = np.random.choice(len(probabilities), p=probabilities)
        return next_queue_id if next_queue_id != len(probabilities) else None
    
    def simulate(self):
        """
        Simulates the network and also schedules the first arrival. 
        """
        # Schedule the first arrival
        arrival_time = self.agents.generate_interarrival_time(self.arrival_rate)
        self.agent_counter += 1  # Generate a unique ID for each agent
        agent = Agent(arrival_time, self.agent_counter)

        initial_queue_id = 0  # Assuming the first agent starts at queue 0 #need to change this to stage_id
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
    service_rates = [1.5, 1.5, 2, 2]
    max_time = 10000
    num_servers = [1, 1, 1, 1]
    prob_matrix = [[0.0, 0.2, 0.0, 0.8], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0], [0.0,0.0,0.0,0.0]]

    np.random.seed(2)
    network = OpenQueueNetwork(arrival_rate, service_rates, max_time, num_servers, prob_matrix)
    agents_data = network.simulate()   
    
    print(agents_data)
    
    np.save("/home/romesh-prasad/ONR/Queuing_system/DE_sim/Data/agent_1_1_1_1(1)",agents_data)

    # Visualize the results
    network.visualize()
