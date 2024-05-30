# DE_sim
This repository is for discrete event simulation using priority queue in python

To run the code
# Servers in parallel
## Single server priority queue
Please clone the git repository: `https://github.com/romeshprasad/DE_sim.git` in the command shell or visual studio code or any other IDEs.\
Navigate to the folder where the repository is cloned.\
To run simply type/copy on your command line  `python .\1_server_priority_queue.py`

This section of the code doesn't handle the edge cases.\


## "n" numbers of server priority queue
Please clone the git repository: `https://github.com/romeshprasad/DE_sim.git` in the command shell or visual studio code or any other IDEs.\
Navigate to the folder where the repository is cloned.\
To run simply type/copy on your command line  `python .\n_server_priority_queue.py`\

This code handles following edge cases: (The edge cases are identified with the help of ChatGPT) \ 
1.) Customer Abandonment: Customers leave the queue if they wait too long.\
2.) Zero Arrival Rate (lam_bda = 0): Simulation should handle scenarios with no new customers arriving.\
3.) Zero Service Rate (mu = 0): Simulation should handle scenarios where servers cannot service customers.\
4.) Simulation End Time: Ensure the simulation ends correctly at max_clock.\
5.) Initial Conditions: Allow starting with customers already in the system.\

The above code with n=1 becomes the single server priority queue

# Servers in series
Upcoming
