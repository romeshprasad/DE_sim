import numpy as np

data = np.load('DE_sim/Data/agent_1_1_1_1(1).npy')

def analyze_jackson_network(data):
    # Extract columns from the data
    agent_id = data[:, 0]
    arrival_time = data[:, 1]
    service_start_time = data[:, 2]
    departure_time = data[:, 3]
    server_id = data[:, 4]
    queue_id = data[:, 5]
    queue_length_on_arrival = data[:, 6]
    
    # Calculate waiting times
    waiting_time = service_start_time - arrival_time
    
    # Calculate total time in the system for each agent
    unique_agents = np.unique(agent_id) 
    total_time_in_system = {}
    """
    For each agent the total time in system is 
    arrival time in the system - departure time from the system
    """
    for agent in unique_agents:
        agent_times = departure_time[agent_id == agent]
        total_time_in_system[agent] = agent_times.max() - arrival_time[agent_id == agent].min() 
    
    # Analyze queue lengths
    unique_queues = np.unique(queue_id)
    queue_lengths = {queue: queue_length_on_arrival[queue_id == queue].mean() for queue in unique_queues}
    
    # Analyze waiting times
    average_waiting_times = {queue: waiting_time[queue_id == queue].mean() for queue in unique_queues}
    
    # Calculate server utilization per queue
    server_utilization = {}
    total_observation_time = departure_time.max() - arrival_time.min()
    for queue in unique_queues:
        busy_time = (departure_time[queue_id == queue] - service_start_time[queue_id == queue]).sum()
        server_utilization[queue] = busy_time / total_observation_time

    return {
        "time_in_system_each_agent": total_time_in_system,
        "total_time_in_system": sum(total_time_in_system.values()),
        "average_waiting_times_per_queue": average_waiting_times,
        "total_waiting_time" : sum(average_waiting_times.values()),
        "queue_lengths_on_arrival": queue_lengths,
        "total_queue_length_in_system": sum(queue_lengths.values()),
        "server_utilization": server_utilization,
        "average_utilization": sum(server_utilization.values())/len(unique_queues)
    }



result = analyze_jackson_network(data)
print("time_in_system_each_agent:", result["time_in_system_each_agent"])
print("total_time_in_system:", result["total_time_in_system"])
print("average_waiting_times_per_queue:", result["average_waiting_times_per_queue"])
print("total_waiting_time:", result["total_waiting_time"])
print("queue_lengths_on_arrival:", result["queue_lengths_on_arrival"])
print("total_queue_length_in_system:", result["total_queue_length_in_system"])
print("server_utilization:", result["server_utilization"])
print("average_utilization:", result["average_utilization"])
