import numpy as np
import matplotlib.pyplot as plt

# data = np.load('Data from 2 servers.npy')

# # arrival_rate_1 = [data[i,0] for i in range(len(data)) if data[i,4] == 0]
# # print(len(arrival_rate_1))

# # arrival_rate_2 = [data[i,0] for i in range(len(data)) if data[i,4] == 1]
# # print(len(arrival_rate_2))

# # queue_length_1 = [data[i,3] for i in range(len(data)) if data[i,4] == 0]
# # print(len(queue_length_1))

# arrival_rate_1 = []
# queue_length_1 = []
# arrival_rate_2 = []
# queue_length_2 = []


# num_arrivals = 2
# #for i in range(num_arrivals):
# for j in range(len(data)):
#     if data[j,4] == 0:
#         arrival_rate , queue_length = data[j,0] , data[j,3]
#         arrival_rate_1.append(arrival_rate)
#         queue_length_1.append(queue_length)
#     else:
#         arrival_rate_2.append(data[j,0])
#         queue_length_2.append(data[j,3])    


        
# plt.figure(figsize=(12, 6))
# plt.plot(arrival_rate_1, queue_length_1, drawstyle='steps-post', label = 'q_server_1')
# plt.plot(arrival_rate_2, queue_length_2, drawstyle='steps-post', label = 'q_seerver_2')
# plt.xlabel('Time')
# plt.ylabel('Queue Length')
# plt.title('Queue Length Over Time')
# plt.grid(True)
# plt.legend()
# plt.show()        
        
# #import numpy as np
# #import matplotlib.pyplot as plt

# # Load the data
# #data = np.load('Data from 2 servers.npy')

# # Extract unique server IDs
# server_ids = np.unique(data[:, 4])

# # Initialize dictionaries to store arrival rates and queue lengths for each server
# arrival_rates = {server_id: [] for server_id in server_ids}
# queue_lengths = {server_id: [] for server_id in server_ids}


# Populate the dictionaries with data
# for entry in data:
#     server_id = entry[4]
#     arrival_rate = entry[0]
#     queue_length = entry[3]
#     arrival_rates[server_id].append(arrival_rate)
#     queue_lengths[server_id].append(queue_length)

# # Plot the data
# plt.figure(figsize=(12, 6))

# for server_id in server_ids:
#     plt.plot(arrival_rates[server_id], queue_lengths[server_id], drawstyle='steps-post', label=f'q_server_{int(server_id)}')

# plt.xlabel('Time')
# plt.ylabel('Queue Length')
# plt.title('Queue Length Over Time')
# plt.grid(True)
# plt.legend()
# plt.show()


        
# if num_servers == 1:

#     # Theoretical values
#     rho = self.arrival_rate / self.service_rate
#     L = rho / (1 - rho)
#     W = 1 / (self.service_rate - self.arrival_rate)
#     L_q = (rho ** 2) / (1 - rho)
#     W_q = self.arrival_rate / (self.service_rate * (self.service_rate - self.arrival_rate))



#     print('\nTheoretical steady-state values:')
#     print(f'Average number of customers in system: {L:.2f}')
#     print(f'Average time spent in system: {W:.2f}')
#     print(f'Average time spent in queue: {W_q:.2f}')
#     print(f'Average time spent in service: {1 / self.service_rate:.2f}')
    
# else:

from matplotlib import pyplot as plt, animation
import networkx as nx

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

fig = plt.figure()

# Create a MultiDiGraph instead of a DiGraph
G = nx.MultiDiGraph()

master_list = [[0, "None", "None", "None"], [1, "Arrival", 0, 1], [2, "Arrival", 0, 1], [3, "Departure", 1, 2], [4, "Departure", 2, 3]]

x = ["Arrival", "Stage 1", "Stage 2", "Departure"]
G.add_nodes_from(x)

# Define a fixed layout
pos = {
    "Arrival": (0, 0),
    "Stage 1": (1, 0),
    "Stage 2": (2, 0),
    "Departure": (3, 0)
}

# To track the current edges and simulate movement
current_edges = []


def animate(frame):
    fig.clear()
    print(frame)
    if frame > 0:
        # Remove the edge from the previous frame if it exists
        prev_num1 = master_list[frame][2]
        prev_num2 = master_list[frame][3]
        if (x[prev_num1], x[prev_num2]) in current_edges:
            current_edges.remove((x[prev_num1], x[prev_num2]))
    
    # Add the edge for the current frame
    num1 = master_list[frame + 1][2]
    num2 = master_list[frame + 1][3]
    current_edges.append((x[num1], x[num2]))
    
    G_temp = nx.MultiDiGraph()
    G_temp.add_nodes_from(x)
    G_temp.add_edges_from(current_edges)
    
    nx.draw(G_temp, pos=pos, with_labels=True, node_size=700, node_color="skyblue", font_size=10, font_color="black", edge_color="gray")

ani = animation.FuncAnimation(fig, animate, frames=len(master_list) - 1, interval=1000, repeat=True)
plt.show()
print(current_edges)

# from matplotlib import pyplot as plt, animation
# import networkx as nx
# import numpy as np

# plt.rcParams["figure.figsize"] = [7.50, 3.50]
# plt.rcParams["figure.autolayout"] = True

# fig = plt.figure()

# # Create a MultiDiGraph instead of a DiGraph
# G = nx.MultiDiGraph()

# master_list = [[0, "None", "None", "None"], [1, "Arrival", 0, 1], [2, "Arrival", 0, 1], [3, "Departure", 1, 2], [4, "Departure", 2, 3]]

# x = ["Arrival", "Stage 1", "Stage 2", "Departure"]
# G.add_nodes_from(x)

# # Define a fixed layout
# pos = {
#     "Arrival": (0, 0),
#     "Stage 1": (1, 0),
#     "Stage 2": (2, 0),
#     "Departure": (3, 0)
# }

# # To track the current edges and simulate movement
# current_edges = []

# def curved_edges(G, pos, ax, connectionstyle='arc3, rad=0.2'):
#     for u, v, data in G.edges(data=True):
#         rad = data['rad'] if 'rad' in data else 0.2
#         ax.annotate('',
#                     xy=pos[v], xycoords='data',
#                     xytext=pos[u], textcoords='data',
#                     arrowprops=dict(arrowstyle="-|>", alpha=0.5, color='gray',
#                                     shrinkA=5, shrinkB=5,
#                                     patchA=None, patchB=None,
#                                     connectionstyle=f"arc3,rad={rad}"))

# def animate(frame):
#     fig.clear()
    
#     if frame > 0:
#         # Remove the edge from the previous frame if it exists
#         prev_num1 = master_list[frame][2]
#         prev_num2 = master_list[frame][3]
#         if (x[prev_num1], x[prev_num2]) in current_edges:
#             current_edges.remove((x[prev_num1], x[prev_num2]))
    
#     # Add the edge for the current frame
#     num1 = master_list[frame + 1][2]
#     num2 = master_list[frame + 1][3]
#     current_edges.append((x[num1], x[num2]))
    
#     G_temp = nx.MultiDiGraph()
#     G_temp.add_nodes_from(x)
#     for edge in current_edges:
#         rad = 0.2 * current_edges.count(edge)  # Different curvature for multiple edges
#         G_temp.add_edge(edge[0], edge[1], rad=rad)
    
#     nx.draw(G_temp, pos=pos, with_labels=True, node_size=700, node_color="skyblue", font_size=10, font_color="black", edge_color="gray")
    
#     ax = plt.gca()
#     curved_edges(G_temp, pos, ax)

# ani = animation.FuncAnimation(fig, animate, frames=len(master_list) - 1, interval=1000, repeat=True)
# plt.show()



#G.add_nodes_from([0, 1, 2, 3, 4])



# def animate(frame):
#    fig.clear()
#    num1 = [master_list[1][]]

#    G.add_edges_from([(x[num1], x[num2])])
#    nx.draw(G, with_labels=True)

# ani = animation.FuncAnimation(fig, animate, frames=6, interval=1000, repeat=True)

#plt.show()

