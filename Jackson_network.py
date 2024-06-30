import numpy as np
import heapq
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import networkx as nx

class Agent:
    def __init__(self, arrival_time, agent_id, queue_path):
        self.arrival_time = arrival_time
        self.service_start_time = None
        self.departure_time = None
        self.queue_length_on_arrival = None
        self.server_id = None
        self.agent_id = agent_id
        self.current_queue = 0
        self.queue_path = queue_path

    def __lt__(self, other):
        return self.arrival_time < other.arrival_time

class Server:
    def __init__(self, server_id):
        self.server_id = server_id
        self.is_busy = False
        self.current_agent = None

class MMmQueue:
    def __init__(self, arrival_rate, service_rate, max_time, num_servers, max_queue_length):
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.max_time = max_time
        self.num_servers = num_servers
        self.queue = []
        self.time = 0
        self.event_queue = []
        self.agents_data = []
        self.servers = [Server(i) for i in range(num_servers)]
        self.agent_counter = 0
        self.max_queue_length = max_queue_length

        self.total_time_in_system = 0
        self.total_time_in_queue = 0
        self.total_time_in_service = 0
        self.total_arrivals = 0
        self.total_departures = 0
        self.blocked_customers = 0
        self.last_event_time = 0
        self.queue_length_data = []

    def generate_interarrival_time(self):
        return round(np.random.exponential(1.0 / self.arrival_rate), 3)

    def generate_service_time(self):
        return round(np.random.exponential(1.0 / self.service_rate), 3)

    def handle_arrival(self, agent, current_time):
        self.update_statistics(current_time)
        self.queue_length_data.append((current_time, len(self.queue)))
        self.total_arrivals += 1
        agent.queue_length_on_arrival = len(self.queue)
        free_server = next((server for server in self.servers if not server.is_busy), None)
        if free_server:
            free_server.is_busy = True
            free_server.current_agent = agent
            agent.service_start_time = current_time
            agent.server_id = free_server.server_id
            service_time = self.generate_service_time()
            agent.departure_time = current_time + service_time
            heapq.heappush(self.event_queue, (agent.departure_time, 'departure', agent))
        elif len(self.queue) < self.max_queue_length:
            self.queue.append(agent)
        else:
            self.blocked_customers += 1

    def handle_departure(self, agent, current_time):
        self.update_statistics(current_time)
        self.queue_length_data.append((current_time, len(self.queue)))
        self.total_departures += 1
        self.agents_data.append([
            agent.arrival_time,
            agent.service_start_time,
            current_time,
            agent.queue_length_on_arrival,
            agent.server_id,
            agent.agent_id
        ])

        server = self.servers[agent.server_id]
        server.is_busy = False
        server.current_agent = None
        
        if self.queue:
            next_agent = self.queue.pop(0)
            server.is_busy = True
            server.current_agent = next_agent
            next_agent.service_start_time = current_time
            next_agent.server_id = server.server_id
            service_time = self.generate_service_time()
            next_agent.departure_time = current_time + service_time
            heapq.heappush(self.event_queue, (next_agent.departure_time, 'departure', next_agent))

    def update_statistics(self, current_time):
        time_diff = current_time - self.last_event_time
        self.total_time_in_system += time_diff * len(self.queue)
        self.total_time_in_queue += time_diff * max(0, len(self.queue) - self.num_servers)
        self.total_time_in_service += time_diff * min(len(self.queue), self.num_servers)
        self.last_event_time = current_time

    def calculate_statistics(self, current_time):
        self.update_statistics(current_time)
        total_time = current_time
        L = self.total_time_in_system / total_time if total_time > 0 else 0
        L_q = self.total_time_in_queue / total_time if total_time > 0 else 0
        L_s = self.total_time_in_service / total_time if total_time > 0 else 0
        W = L / self.arrival_rate if self.arrival_rate > 0 else 0
        W_q = L_q / self.arrival_rate if self.arrival_rate > 0 else 0
        W_s = L_s / self.arrival_rate if self.arrival_rate > 0 else 0
        
        return {
            'L': L,
            'L_q': L_q,
            'L_s': L_s,
            'W': W,
            'W_q': W_q,
            'W_s': W_s,
            'Blocked customers': self.blocked_customers,
            'Total arrivals': self.total_arrivals,
            'Total departures': self.total_departures
        }

class QueueAnimator:
    def __init__(self, max_time, num_queues):
        self.fig, self.axs = plt.subplots(num_queues, 1, figsize=(10, 4*num_queues))
        if num_queues == 1:
            self.axs = [self.axs]
        self.lines = [ax.plot([], [], 'ro-')[0] for ax in self.axs]
        self.max_time = max_time
        self.num_queues = num_queues

    def init(self):
        for ax in self.axs:
            ax.set_xlim(0, self.max_time)
            ax.set_ylim(0, 1)  # Start with a small range
            ax.set_xlabel('Time')
            ax.set_ylabel('Queue Length')
        self.axs[0].set_title('Queue Lengths Over Time')
        return self.lines

    def update(self, frame, queues):
        for i, queue in enumerate(queues):
            times, lengths = zip(*queue.queue_length_data)
            self.lines[i].set_data(times[:frame], lengths[:frame])
            self.axs[i].set_title(f'Queue {i} Length')
            self.axs[i].relim()
            self.axs[i].autoscale_view()
        return self.lines

    def animate(self, queues):
        max_frames = max(len(queue.queue_length_data) for queue in queues)
        anim = FuncAnimation(self.fig, self.update, frames=range(1, max_frames + 1),
                             init_func=self.init, fargs=(queues,), blit=False, interval=1000, repeat=False)
        plt.tight_layout()
        plt.show(block=False)

class JacksonNetwork:
    def __init__(self, num_queues, arrival_rates, service_rates, routing_probabilities, max_time, num_servers, max_queue_lengths):
        self.queues = [MMmQueue(arrival_rates[i], service_rates[i], max_time, num_servers[i], max_queue_lengths[i]) for i in range(num_queues)]
        self.routing_probabilities = routing_probabilities
        self.max_time = max_time
        self.event_queue = []
        self.time = 0
        self.agent_counter = 0
        self.animator = QueueAnimator(max_time, num_queues)

    def simulate(self):
        for i, queue in enumerate(self.queues):
            arrival_time = queue.generate_interarrival_time()
            self.agent_counter += 1
            agent = Agent(arrival_time, self.agent_counter, [i])
            heapq.heappush(self.event_queue, (arrival_time, 'arrival', agent, i))

        while self.event_queue:
            self.time, event_type, agent, queue_index = heapq.heappop(self.event_queue)
            if self.time > self.max_time:
                break

            if event_type == 'arrival':
                self.handle_arrival(agent, queue_index)
            elif event_type == 'departure':
                self.handle_departure(agent, queue_index)

        # Add final data point for each queue
        for queue in self.queues:
            queue.queue_length_data.append((self.max_time, len(queue.queue)))

    def handle_arrival(self, agent, queue_index):
        queue = self.queues[queue_index]
        queue.handle_arrival(agent, self.time)
        next_arrival_time = self.time + queue.generate_interarrival_time()
        if next_arrival_time <= self.max_time:
            self.agent_counter += 1
            next_agent = Agent(next_arrival_time, self.agent_counter, [queue_index])
            heapq.heappush(self.event_queue, (next_arrival_time, 'arrival', next_agent, queue_index))

    def handle_departure(self, agent, queue_index):
        queue = self.queues[queue_index]
        queue.handle_departure(agent, self.time)
        
        next_queue = self.get_next_queue(queue_index)
        if next_queue is not None:
            agent.queue_path.append(next_queue)
            arrival_time = self.time
            heapq.heappush(self.event_queue, (arrival_time, 'arrival', agent, next_queue))

    def get_next_queue(self, current_queue):
        probabilities = self.routing_probabilities[current_queue]
        next_queue = np.random.choice(len(probabilities), p=probabilities)
        return next_queue if next_queue != current_queue else None

    def get_statistics(self):
        return [queue.calculate_statistics(self.max_time) for queue in self.queues]

    def visualize_network(self):
        G = nx.DiGraph()
        
        # Add source node
        G.add_node('Source', pos=(0, 0))
        
        # Add queue nodes
        for i in range(len(self.queues)):
            G.add_node(f'Queue {i}', pos=(1, i - (len(self.queues)-1)/2))
        
        # Add sink node
        G.add_node('Sink', pos=(2, 0))
        
        # Add edges
        for i, queue in enumerate(self.queues):
            G.add_edge('Source', f'Queue {i}', weight=queue.arrival_rate)
            G.add_edge(f'Queue {i}', 'Sink', weight=queue.service_rate)
        
        # Add routing edges
        for i in range(len(self.queues)):
            for j in range(len(self.queues)):
                if i != j and self.routing_probabilities[i][j] > 0:
                    G.add_edge(f'Queue {i}', f'Queue {j}', weight=self.routing_probabilities[i][j])
        
        # Get position layout
        pos = nx.get_node_attributes(G, 'pos')
        
        # Draw the graph
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
                node_size=3000, font_size=10, font_weight='bold')
        
        # Draw edge labels
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
        
        plt.title("Jackson Network Visualization")
        plt.axis('off')
        plt.tight_layout()
        plt.show()

# Example usage
if __name__ == "__main__":
    num_queues = 3
    arrival_rates = [15, 13, 14]  # External arrival rates for each queue
    service_rates = [6, 5, 7]  # Service rates for each queue
    routing_probabilities = [
        [0.0, 0.7, 0.2, 0.1],  # From queue 0: stay, go to queue 1, go to queue 2, exit
        [0.0, 0.0, 0.8, 0.2],  # From queue 1: stay, go to queue 2, exit
        [0.0, 0.0, 0.0, 1.0],  # From queue 2: exit
    ]
    max_time = 10000  # Increased simulation time
    num_servers = [1, 1, 1]  # Number of servers for each queue
    max_queue_lengths = [100, 100, 100]  # Maximum queue lengths

    network = JacksonNetwork(num_queues, arrival_rates, service_rates, routing_probabilities, max_time, num_servers, max_queue_lengths)
    network.simulate()
    statistics = network.get_statistics()

    for i, stats in enumerate(statistics):
        print(f"\nQueue {i} Statistics:")
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")

    # Print some debug information
    for i, queue in enumerate(network.queues):
        print(f"\nQueue {i} data points: {len(queue.queue_length_data)}")
        print(f"First 5 data points: {queue.queue_length_data[:5]}")
        print(f"Last 5 data points: {queue.queue_length_data[-5:]}")
        print(f"Max queue length: {max(length for _, length in queue.queue_length_data)}")

    network.visualize_network()
    network.animator.animate(network.queues)
