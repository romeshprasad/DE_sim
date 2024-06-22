import numpy as np
from matplotlib import pyplot as plt, animation
from openqueue import OpenQueueNetwork
import networkx as nx

num_servers = 5
arrival = 0
departure = num_servers + 1
# Load the dataset
data = np.load('master_queue_1.npy')

print(data)

stages_config = [1,2]

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

fig = plt.figure()

# Create a MultiDiGraph
G = nx.MultiDiGraph()

# Nodes = [0,1,2,3]
# pos = {0: (0,0), 1: (1,0), 2:(2,0), 3:(3,0)}


# Generate nodes and their positions
Nodes = [0]  # Start with the arrival node
pos = {0: (0, 0)}
current_node_index = 1

# Generate nodes and positions for each stage
for stage, num_servers in enumerate(stages_config):
    for server in range(num_servers):
        Nodes.append(current_node_index)
        pos[current_node_index] = (stage + 1, server)
        current_node_index += 1

# Add departure node
Nodes.append(current_node_index)
pos[current_node_index] = (len(stages_config) + 1, 0)
G.add_nodes_from(Nodes)

current_edges = []

def animate(frame):
    
    fig.clear()
    current_edges.clear()
    
    if frame > 0:
        prev_num1 = int(data[frame][1])
        prev_num2 = int(data[frame][2])
        if (Nodes[prev_num1], Nodes[prev_num2]) in current_edges:
            current_edges.remove((Nodes[prev_num1], Nodes[prev_num2]))
            
    num1 = int(data[frame + 1][1])
    num2 = int(data[frame + 1][2])
    current_edges.append((Nodes[num1], Nodes[num2]))
    
    G_temp = nx.MultiDiGraph()
    G_temp.add_nodes_from(Nodes)
    G_temp.add_edges_from(current_edges)
    
    nx.draw(G_temp, pos=pos, with_labels=True, node_size=700, node_color="skyblue", font_size=10, font_color="black", edge_color="gray")

ani = animation.FuncAnimation(fig, animate, frames=len(data) - 1, interval=1000, repeat=True)
plt.show()

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