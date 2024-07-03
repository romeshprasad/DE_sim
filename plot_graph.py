import numpy as np
from matplotlib import pyplot as plt, animation
import networkx as nx

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

fig = plt.figure()

# Create a MultiDiGraph instead of a DiGraph
G = nx.MultiDiGraph()

data = np.load("open_network_1_2.npy")
print(data)

num_servers = [1,2]
def get_node(num_servers):
    # Generate nodes and their positions
    Nodes = [0]  # Start with the arrival node
    pos = {0: (0, 0)} # arrival position
    current_node_index = 1

    # Generate nodes and positions for each stage
    for stage, num_servers in enumerate(num_servers):
        for server in range(num_servers):
            Nodes.append(current_node_index)
            pos[current_node_index] = (stage + 1, server)
            current_node_index += 1
    # Add departure node
    Nodes.append(current_node_index)
    #Add departure pos
    pos[4] = (3,0)
    return Nodes, pos

Nodes , pos = get_node(num_servers)


G.add_nodes_from(Nodes)


# To track the current edges and simulate movement
current_edges = []


def animate(frame):
    fig.clear()
    print(frame)
    if frame > 0:
        # Remove the edge from the previous frame if it exists
        prev_num1 = int(data[frame][3])
        prev_num2 = int(data[frame][4])
        if (Nodes[prev_num1], Nodes[prev_num2]) in current_edges:
            current_edges.remove((Nodes[prev_num1], Nodes[prev_num2]))
    
    # Add the edge for the current frame
    num1 = int(data[frame + 1][3])
    num2 = int(data[frame + 1][4])
    current_edges.append((Nodes[num1], Nodes[num2]))
    
    print(current_edges)
    G_temp = nx.MultiDiGraph()
    G_temp.add_nodes_from(Nodes)
    G_temp.add_edges_from(current_edges)
    
    nx.draw(G_temp, pos=pos, with_labels=True, node_size=700, node_color="skyblue", font_size=10, font_color="black", edge_color="gray")

ani = animation.FuncAnimation(fig, animate, frames=len(data) - 1, interval=1000, repeat=True)
plt.show()
