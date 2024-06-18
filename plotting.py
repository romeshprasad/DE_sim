import matplotlib.pyplot as plt
import numpy as np

agents_data = np.load('Data_from_agent.npy')

def visualize(agents_data):
    # Convert data to a numpy array for easier handling
    data = np.array(agents_data)
    agent_ids = data[:, 0]
    queue_ids = data[:, 1]
    arrival_times = data[:, 2]
    departure_times = data[:, 4]
    queue_lengths = data[:, 5]
    
    plt.figure(figsize=(12, 6))
    for queue_id in np.unique(queue_ids):
        queue_data = data[data[:, 1] == queue_id]
        plt.plot(queue_data[:, 2], queue_data[:, 5], drawstyle='steps-post', label=f'Queue {queue_id}')
    
    plt.xlabel('Time')
    plt.ylabel('Queue Length')
    plt.title('Queue Length Over Time for Different Queues')
    plt.legend()
    plt.grid(True)
    plt.show()
    
if __name__=="__main__":
    v = visualize(agents_data)