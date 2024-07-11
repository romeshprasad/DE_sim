"""
Key changes in this version:
    Node Structure: We now have separate nodes for queues (Q1, Q2, etc.) and servers (S1W1, S1W2, S2W1, etc.).
    Graph Structure: The graph now includes edges from queues to servers and from servers to the next stage's queue.
    Visualization:
        Queue nodes change color based on the number of agents waiting.
        Server nodes change color based on whether they're busy or free.
        Edges show the movement of agents between queues and servers.
    Agent Tracking: We now track whether an agent is in a queue or being served by a specific server.
    Edge Colors:
        Red: Agent moving to or waiting in a queue
        Green: Agent being served
        Blue: Completed paths

This visualization should give a more 
comprehensive view of your queuing system, 
showing both waiting areas and service points. 
The color changes in nodes provide an immediate 
visual cue about the system's current state. 
Remember to adjust the SERVER_CONFIG list to match your actual system configuration. 
You may also want to fine-tune the color scaling for queue nodes based on your expected queue lengths.
"""



import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from typing import Dict, Tuple, List

# Constants
NODE_SIZE = 3000
FONT_SIZE = 8
FRAME_INTERVAL = 100
COLOR_MAP = {
    'queue': plt.cm.YlOrRd,
    'server_busy': 'red',
    'server_free': 'green',
    'default': 'lightblue'
}

# Load simulation data
SIMULATION_DATA = np.load('/home/romesh-prasad/ONR/Queuing_system/DE_sim/Data/convert_agent_1_1_1.npy')
print(SIMULATION_DATA)

# System configuration
SERVER_CONFIG = [1, 1, 1]  # Adjust based on actual configuration
NUM_STAGES = len(SERVER_CONFIG)

def create_network(config: List[int]) -> Tuple[nx.DiGraph, Dict]:
    """Create a network graph based on the given server configuration."""
    G = nx.DiGraph()
    pos = {}
    
    # Add arrival node
    G.add_node('Arrival', pos=(0, 1))
    pos['Arrival'] = (0, 1)

    # Add queue and server nodes for each stage
    for stage, num_workers in enumerate(config):
        queue_node = f'Q{stage+1}'
        G.add_node(queue_node, pos=(0, -(stage*2)))
        pos[queue_node] = (0, -(stage*2))
        
        for worker in range(num_workers):
            server_node = f'S{stage+1}W{worker+1}'
            G.add_node(server_node, pos=(worker - (num_workers-1)/2, -(stage*2+1)))
            pos[server_node] = (worker - (num_workers-1)/2, -(stage*2+1))

    # Add departure node
    G.add_node('Departure', pos=(0, -(len(config)*2+1)))
    pos['Departure'] = (0, -(len(config)*2+1))

    # Add edges
    G.add_edge('Arrival', 'Q1')
    for stage in range(len(config)):
        for worker in range(config[stage]):
            G.add_edge(f'Q{stage+1}', f'S{stage+1}W{worker+1}')
            if stage < len(config) - 1:
                G.add_edge(f'S{stage+1}W{worker+1}', f'Q{stage+2}')
            else:
                G.add_edge(f'S{stage+1}W{worker+1}', 'Departure')

    return G, pos

# Create network graph
G, pos = create_network(SERVER_CONFIG)
print(G, pos)

# Prepare the figure
fig, ax = plt.subplots(figsize=(12, 8))

# Initialize counters for each node
node_counters = {node: 0 for node in G.nodes()}

def update_queue_counts(data: np.ndarray, frame: float) -> Dict[str, int]:
    """Update the count of agents in each queue at the given frame."""
    queue_counts = {f'Q{i+1}': 0 for i in range(NUM_STAGES)}
    for row in data:
        for stage in range(NUM_STAGES):
            queue_start = 0 if stage == 0 else row[f'stage{stage}_exit']
            if queue_start <= frame < row[f'stage{stage+1}_entry']:
                queue_counts[f'Q{stage+1}'] += 1
    return queue_counts

def update_server_status(data: np.ndarray, frame: float) -> Dict[str, str]:
    """Update the status of each server at the given frame."""
    server_status = {f'S{i+1}W{j+1}': 'free' for i in range(NUM_STAGES) for j in range(SERVER_CONFIG[i])}
    for row in data:
        for stage in range(NUM_STAGES):
            if row[f'stage{stage+1}_entry'] <= frame < row[f'stage{stage+1}_exit']:
                server = f'S{stage+1}W{row[f"stage{stage+1}_worker"]}'
                server_status[server] = 'busy'
    return server_status

def update_edge_colors(data: np.ndarray, frame: float) -> List[Tuple[str, str, str]]:
    """Update the colors of edges based on agent movements at the given frame."""
    edge_colors = []
    for row in data:
        for stage in range(NUM_STAGES):
            queue_start = 0 if stage == 0 else row[f'stage{stage}_exit']
            if queue_start <= frame < row[f'stage{stage+1}_entry']:
                if stage == 0:
                    edge_colors.append(('Arrival', f'Q{stage+1}', 'r'))
                else:
                    edge_colors.append((f'S{stage}W{row[f"stage{stage}_worker"]}', f'Q{stage+1}', 'r'))
            elif row[f'stage{stage+1}_entry'] <= frame < row[f'stage{stage+1}_exit']:
                server = f'S{stage+1}W{row[f"stage{stage+1}_worker"]}'
                edge_colors.append((f'Q{stage+1}', server, 'g'))
            elif frame >= row[f'stage{stage+1}_exit']:
                if stage < NUM_STAGES - 1:
                    edge_colors.append((f'S{stage+1}W{row[f"stage{stage+1}_worker"]}', f'Q{stage+2}', 'b'))
                else:
                    edge_colors.append((f'S{stage+1}W{row[f"stage{stage+1}_worker"]}', 'Departure', 'b'))
    return edge_colors

def update_node_counters(data: np.ndarray, frame: float) -> None:
    """Update the counters for each node based on agent movements."""
    global node_counters
    for row in data:
        for stage in range(NUM_STAGES):
            if stage == 0 and frame >= row['stage1_entry'] and node_counters['Arrival'] == 0:
                node_counters['Arrival'] += 1
                node_counters[f'Q{stage+1}'] += 1
            elif frame >= row[f'stage{stage+1}_entry'] and node_counters[f'Q{stage+1}'] == stage:
                node_counters[f'Q{stage+1}'] += 1
            
            if row[f'stage{stage+1}_entry'] <= frame < row[f'stage{stage+1}_exit']:
                server = f'S{stage+1}W{row[f"stage{stage+1}_worker"]}'
                if node_counters[server] == stage:
                    node_counters[server] += 1
            
            if stage == NUM_STAGES - 1 and frame >= row[f'stage{NUM_STAGES}_exit'] and node_counters['Departure'] < row['agent_id']:
                node_counters['Departure'] += 1

def update(frame: float):
    """Update the animation frame."""
    ax.clear()
    ax.set_title(f"Agent Movement Network Graph - Time: {frame:.3f}")
    
    queue_counts = update_queue_counts(SIMULATION_DATA, frame)
    server_status = update_server_status(SIMULATION_DATA, frame)
    edge_colors = update_edge_colors(SIMULATION_DATA, frame)
    update_node_counters(SIMULATION_DATA, frame)

    # Draw nodes
    node_colors = []
    for node in G.nodes():
        if node.startswith('Q'):
            count = queue_counts.get(node, 0)
            color = COLOR_MAP['queue'](min(count / 5, 1))
        elif node.startswith('S'):
            color = COLOR_MAP['server_busy'] if server_status.get(node) == 'busy' else COLOR_MAP['server_free']
        else:
            color = COLOR_MAP['default']
        node_colors.append(color)
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=NODE_SIZE, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=FONT_SIZE, ax=ax)
    
    # Draw colored edges
    for edge in set(edge_colors):
        nx.draw_networkx_edges(G, pos, edgelist=[edge[:2]], edge_color=edge[2], width=2, arrows=True, ax=ax)
    
    # Draw inactive edges
    all_edges = set(G.edges())
    colored_edges = set(edge[:2] for edge in edge_colors)
    grey_edges = all_edges - colored_edges
    nx.draw_networkx_edges(G, pos, edgelist=grey_edges, edge_color='lightgrey', width=1, arrows=True, ax=ax)
    
    # Add counter labels above nodes
    for node, (x, y) in pos.items():
        ax.text(x, y + 0.1, f'{node_counters[node]}', ha='center', va='center')
    
    ax.axis('off')
    
    print(f"Frame {frame:.3f}")
    print(f"Queue counts: {queue_counts}")
    print(f"Server status: {server_status}")
    print(f"Node counters: {node_counters}")
    print("====================")

# Create the animation
anim = animation.FuncAnimation(fig, update, frames=np.arange(0, 100, 0.1), interval=FRAME_INTERVAL, repeat=False)

plt.tight_layout()
plt.show()
