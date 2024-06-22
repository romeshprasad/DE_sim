# import numpy as np
# from matplotlib import pyplot as plt, animation
# import networkx as nx


# # Load the dataset
# data = np.array([
#     [1.0, 0.129, 0.129, 0.479, 0.0, 0.0, 0.0],
#     [1.0, 0.479, 0.479, 0.757, 0.0, 1.0, 0.0],
#     [3.0, 2.834, 2.834, 3.015, 1.0, 0.0, 0.0],
#     [5.0, 3.526, 3.526, 4.27, 2.0, 0.0, 0.0],
#     [6.0, 4.19, 4.27, 4.312, 2.0, 0.0, 0.0],
#     [3.0, 3.015, 3.015, 4.504, 0.0, 1.0, 0.0],
#     [5.0, 4.27, 4.504, 4.798, 0.0, 1.0, 0.0],
#     [4.0, 3.22, 3.22, 4.918, 1.0, 0.0, 0.0],
#     [2.0, 2.294, 2.294, 5.053, 0.0, 0.0, 0.0],
#     [6.0, 4.312, 4.798, 5.514, 0.0, 1.0, 1.0],
#     [8.0, 4.825, 4.918, 5.822, 1.0, 0.0, 0.0],
#     [7.0, 4.806, 4.806, 5.829, 2.0, 0.0, 0.0],
#     [4.0, 4.918, 5.514, 6.489, 0.0, 1.0, 0.0],
#     [2.0, 5.053, 6.489, 6.727, 0.0, 1.0, 1.0]
# ])

# # Configuration for stages and servers
# stages_config = [3, 1]  # Example for a 2-stage process with 3 servers at stage 1 and 1 server at stage 2

# plt.rcParams["figure.figsize"] = [7.50, 3.50]
# plt.rcParams["figure.autolayout"] = True

# fig = plt.figure()

# # Create a MultiDiGraph
# G = nx.MultiDiGraph()

# # Generate nodes and their positions
# Nodes = [0]  # Start with the arrival node
# pos = {0: (0, 0)}
# current_node_index = 1

# # Generate nodes and positions for each stage
# for stage, num_servers in enumerate(stages_config):
#     for server in range(num_servers):
#         Nodes.append(current_node_index)
#         pos[current_node_index] = (stage + 1, server)
#         current_node_index += 1

# # Add departure node
# Nodes.append(current_node_index)
# pos[current_node_index] = (len(stages_config) + 1, 0)
# G.add_nodes_from(Nodes)

# current_edges = []

# def get_node_id(stage_id, server_id):
#     if stage_id == 0:
#         return 0
#     offset = sum(stages_config[:int(stage_id)]) + 1
#     print(offset)
#     return offset + int(server_id)


# def animate(frame):
#     fig.clear()
#     current_edges.clear()
    
#     if frame > 0:
#         prev_num1 = int(data[frame][4])  # previous server_id
#         prev_stage1 = int(data[frame][5])  # previous stage_id
#         prev_source = get_node_id(prev_stage1, prev_num1)
        
#         prev_num2 = int(data[frame][4])  # next server_id (same as previous)
#         prev_stage2 = int(data[frame][5]) + 1  # next stage_id (incremented by 1)
#         prev_target = get_node_id(prev_stage2, prev_num2)
        
#         if (prev_source, prev_target) in current_edges:
#             current_edges.remove((prev_source, prev_target))
#     breakpoint
    
#     num1 = int(data[frame + 1][4])
#     stage1 = int(data[frame + 1][5])
#     source = get_node_id(stage1, num1)
    
#     num2 = int(data[frame + 1][4])
#     stage2 = int(data[frame + 1][5]) + 1
#     target = get_node_id(stage2, num2)
    
#     current_edges.append((source, target))
    
#     G_temp = nx.MultiDiGraph()
#     G_temp.add_nodes_from(Nodes)
#     G_temp.add_edges_from(current_edges)
    
#     nx.draw(G_temp, pos=pos, with_labels=True, node_size=700, node_color="skyblue", font_size=10, font_color="black", edge_color="gray")

# ani = animation.FuncAnimation(fig, animate, frames=len(data) - 1, interval=1000, repeat=True)
# plt.show()



import numpy as np
import pandas as pd

# Sample dataset
data = np.array([
    [1.0, 0.129, 0.129, 0.479, 0.0, 0.0, 0.0],
    [1.0, 0.479, 0.479, 0.757, 0.0, 1.0, 0.0],
    [3.0, 2.834, 2.834, 3.015, 1.0, 0.0, 0.0],
    [5.0, 3.526, 3.526, 4.27, 2.0, 0.0, 0.0],
    [6.0, 4.19, 4.27, 4.312, 2.0, 0.0, 0.0],
    [3.0, 3.015, 3.015, 4.504, 0.0, 1.0, 0.0],
    [5.0, 4.27, 4.504, 4.798, 0.0, 1.0, 0.0],
    [4.0, 3.22, 3.22, 4.918, 1.0, 0.0, 0.0],
    [2.0, 2.294, 2.294, 5.053, 0.0, 0.0, 0.0],
    [6.0, 4.312, 4.798, 5.514, 0.0, 1.0, 1.0],
    [8.0, 4.825, 4.918, 5.822, 1.0, 0.0, 0.0],
    [7.0, 4.806, 4.806, 5.829, 2.0, 0.0, 0.0],
    [4.0, 4.918, 5.514, 6.489, 0.0, 1.0, 0.0],
    [2.0, 5.053, 6.489, 6.727, 0.0, 1.0, 1.0]
])

# Configuration for stages and servers
stages_config = [3, 1]

# Define nodes
Nodes = [0]  # Arrival node
for stage, num_servers in enumerate(stages_config):
    for _ in range(num_servers):
        Nodes.append(len(Nodes))
Nodes.append(len(Nodes))  # Departure node

# Helper function to get the node ID
def get_node_id(stage_id, server_id):
    if stage_id == 0:
        return 0  # Arrival node
    offset = sum(stages_config[:int(stage_id)]) + 1
    return offset + int(server_id)

# Process the data to create the formatted dataset
formatted_data = []

for row in data:
    agent_id, arrival_time, service_start_time, departure_time, server_id, stage_id, queue_len_on_arrival = row
    
    # Arrival event
    formatted_data.append([arrival_time, 0, get_node_id(stage_id, server_id)])
    
    # Service start event (if different from arrival time)
    if service_start_time != arrival_time:
        formatted_data.append([service_start_time, get_node_id(stage_id, server_id), get_node_id(stage_id, server_id)])
    
    # Departure event
    formatted_data.append([departure_time, get_node_id(stage_id, server_id), len(Nodes) - 1])

# Convert to DataFrame and sort by time
formatted_df = pd.DataFrame(formatted_data, columns=["time", "source", "target"])
formatted_df.sort_values(by="time", inplace=True)

print(formatted_df)
