import numpy as np

# Load the data
data = np.load('/home/romesh-prasad/ONR/Queuing_system/DE_sim/Data/agent_1_1_1.npy')

# Define column indices for easier reference
AGENT_ID = 0
ARRIVAL_TIME = 1
SERVICE_START_TIME = 2
DEPARTURE_TIME = 3
SERVER_ID = 4
QUEUE_ID = 5

# Define the server configuration
# This should be a list where each element represents the number of servers in that stage
SERVER_CONFIG = [1,1,1]  # Change this according to your system configuration
# For example: [2, 1] for 2 servers in stage 1 and 1 in stage 2
# Or [1, 2, 3] for 1 server in stage 1, 2 in stage 2, and 3 in stage 3

# Calculate the total number of stages
NUM_STAGES = len(SERVER_CONFIG)

# Function to generate the full path
def get_full_path(stage_workers, server_config):
    path = ["0"]
    current_server = 0
    for i, num_servers in enumerate(server_config):
        current_server += num_servers
        path.append(str(current_server - num_servers + stage_workers[i]))
    path.append(str(current_server + 1))
    return "-".join(path)

# Create a list to store the results
result = []

# Get unique agent IDs
agent_ids = np.unique(data[:, AGENT_ID])

for agent_id in agent_ids:
    # Get all rows for this agent
    agent_data = data[data[:, AGENT_ID] == agent_id]
    
    # Check if we have data for all stages
    if len(agent_data) < NUM_STAGES:
        print(f"Warning: Agent {agent_id} does not have data for all stages. Skipping.")
        continue
    
    # Sort by arrival time
    agent_data = agent_data[agent_data[:, ARRIVAL_TIME].argsort()]
    
    # Initialize lists to store stage data
    stage_entry_times = []
    stage_exit_times = []
    stage_workers = []
    
    # Extract data for all stages
    for stage in range(NUM_STAGES):
        stage_data = agent_data[agent_data[:, QUEUE_ID] == stage]
        if len(stage_data) == 0:
            print(f"Warning: No Stage {stage+1} data for Agent {agent_id}. Skipping.")
            break
        stage_row = stage_data[0]
        stage_entry_times.append(stage_row[ARRIVAL_TIME])
        stage_exit_times.append(stage_row[DEPARTURE_TIME])
        stage_workers.append(int(stage_row[SERVER_ID]))
    
    # Check if we have data for all stages
    if len(stage_entry_times) < NUM_STAGES:
        continue
    
    # Append the data to the result list
    result_row = [float(agent_id)]  # Convert to Python float
    for i in range(NUM_STAGES):
        result_row.extend([
            float(stage_entry_times[i]),  # Convert to Python float
            float(stage_exit_times[i]),   # Convert to Python float
            int(stage_workers[i] + 1)     # Convert to Python int
        ])
    
    # Generate and append the full path
    full_path = get_full_path([int(worker + 1) for worker in stage_workers], SERVER_CONFIG)
    result_row.append(full_path)
    
    result.append(result_row)

# Create a dynamic dtype based on the number of stages
dtype = [('agent_id', 'f8')]
for i in range(NUM_STAGES):
    dtype.extend([
        (f'stage{i+1}_entry', 'f8'),
        (f'stage{i+1}_exit', 'f8'),
        (f'stage{i+1}_worker', 'i4')
    ])
# Add the full_path to the dtype
max_path_length = len(get_full_path([max(SERVER_CONFIG) for _ in range(NUM_STAGES)], SERVER_CONFIG))
dtype.append(('full_path', f'U{max_path_length}'))

# Convert the result list to a NumPy structured array
result_array = np.array([(tuple(row[:-1]) + (row[-1],)) for row in result], dtype=dtype)

# Sort the array by agent_id
result_array.sort(order='agent_id')

# Save the result array
np.save('/home/romesh-prasad/ONR/Queuing_system/DE_sim/Data/convert_agent_1_1_1.npy', result_array)

# Print the result array
print(result_array)

# Create a formatted string representation of the table
headers = ["agent_id"]
for i in range(NUM_STAGES):
    headers.extend([f"stage{i+1}_entry", f"stage{i+1}_exit", f"stage{i+1}_worker"])
headers.append("full_path")

table_str = " | ".join(headers) + "\n"
table_str += "-" * (len(headers) * 15) + "\n"

for row in result_array:
    formatted_row = [f"{row['agent_id']:<8}"]
    for i in range(NUM_STAGES):
        formatted_row.extend([
            f"{row[f'stage{i+1}_entry']:<12.3f}",
            f"{row[f'stage{i+1}_exit']:<11.3f}",
            f"{row[f'stage{i+1}_worker']:<13}"
        ])
    formatted_row.append(row['full_path'])
    table_str += " | ".join(formatted_row) + "\n"

print(table_str)

# If you want to save this to a text file:
# with open('agent_paths.txt', 'w') as f:
#     f.write(table_str)

