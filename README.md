# DE_sim
This repository simulates discrete event simulations for priority queues in Python. The library is still under development. The current implementation allows for the simulation of Jackson networks, as well as parallel and series networks. You can validate the simulation models using mathematical methods.

To run the code
# Servers in parallel
## Single server priority queue
To run  `python .\1_server_priority_queue.py`

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
To run the code please clone as shown above and navigate to the directory and copy/type the following command `python .\n_series_server_priority_queue.py` \
In this code we have defined a variable 
> service_rates. 

Here the users can put a 
>list of service time\

Current code doesnot consider edge cases. It will be added as we move forward
