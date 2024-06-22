import numpy as np
from simulate import simulator
# from queue_simulation.simulator import Simulator
# from queue_simulation.visualize import Visualizer

if __name__ == "__main__":
    arrival_rate = 1.0
    service_rates = [1, 1.5]
    max_time = 10
    num_servers = [1, 2]
    prob_matrix = [[0.0, 1.0], [0.0, 0.0]]

    np.random.seed(2)
    sim = simulator(arrival_rate, service_rates, max_time, num_servers, prob_matrix)
    agents_data, master_queue = sim.simulate()
    print(agents_data, master_queue)

    np.save("master_queue_1", master_queue)
    #Visualizer.visualize(agents_data)