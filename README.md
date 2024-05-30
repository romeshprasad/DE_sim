# DE_sim
This repository is for discrete event simulation

To run the code 
## Servers in paralle
# Single server priority queue
Please clone the git repository: `https://github.com/romeshprasad/DE_sim.git` in the command shell or visual studio code or any other IDEs.\
Navigate to the folder where the repository is cloned.\
To run simply type/copy on your command line  `python .\1_server_priority_queue.py`


# Any number of server priority queue
Please clone the git repository: `https://github.com/romeshprasad/DE_sim.git` in the command shell or visual studio code or any other IDEs.\
Navigate to the folder where the repository is cloned.\
To run simply type/copy on your command line  `python .\n_server_priority_queue.py`\
This code handles following edge cases: \
1.) Customer Abandonment: Customers leave the queue if they wait too long.\
2.) Zero Arrival Rate (λ = 0): Simulation should handle scenarios with no new customers arriving.\
3.) Zero Service Rate (μ = 0): Simulation should handle scenarios where servers cannot service customers.\
4.) Simulation End Time: Ensure the simulation ends correctly at max_clock.\
5.) Initial Conditions: Allow starting with customers already in the system.\