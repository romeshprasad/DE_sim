class fetch_data():
    def __init__(self) -> None:
        self.master_queue = [(0, "source", "target", "event_type")]
    
    def get_node(self):
        # Generate nodes and their positions
        Nodes = [0]  # Start with the arrival node
        pos = {0: (0, 0)}
        current_node_index = 1

        # Generate nodes and positions for each stage
        for stage, num_servers in enumerate(self.num_servers):
            for server in range(num_servers):
                Nodes.append(current_node_index)
                pos[current_node_index] = (stage + 1, server)
                current_node_index += 1
        # Add departure node
        Nodes.append(current_node_index)
        return Nodes, pos

    def get_index_from_list(self, worker_number, stage_number, num_servers):
    # Initialize the offset for the current stage
        offset = 1  # Start from 1 because 0 is reserved for arrival
        
        # Calculate the offset by summing the number of servers in previous stages
        for stage in range(stage_number):
            offset += num_servers[stage]
        
        # The index in the list is the offset plus the worker number
        index = offset + worker_number
        print(f"Worker number: {worker_number}, Stage number: {stage_number}")
        total_servers = sum(num_servers)
        if index < 1 or index > total_servers:
            raise ValueError(f"Invalid index: {index}. Worker number: {worker_number}, Stage number: {stage_number}")
        
        return index
    
    def master_q(self,agent,queue_id, server_id, event_type):
        Nodes, pos = self.get_node()
        server_id = agent.server_id if agent.server_id is not None else 0

        if event_type == "Arrival":
            if queue_id == 0:
                source = Nodes[0]  # Arrival node
                target = Nodes[self.get_index_from_list(server_id, queue_id, self.num_servers)]
            else:
                source = Nodes[self.get_index_from_list(server_id, queue_id - 1, self.num_servers)]
                target = Nodes[self.get_index_from_list(server_id, queue_id, self.num_servers)]
                
            self.master_queue.append([self.time, source, target, 'arrival'])
            
            print(f"Arrival - Time: {self.time}, Agent ID: {agent.agent_id}, Source: {source}, target: {target}, Queue ID: {queue_id}")
        else:  #deaprture
            if queue_id == len(self.num_servers) - 1:
                source = Nodes[self.get_index_from_list(server_id, queue_id, self.num_servers)]
                target = Nodes[-1]  # Departure node
                
            else:
                source = Nodes[self.get_index_from_list(server_id, queue_id, self.num_servers)]
                target = Nodes[self.get_index_from_list(server_id, queue_id + 1, self.num_servers)]
            
            print(f"Departure - Time: {self.time}, Agent ID: {agent.agent_id}, Source: {source}, target: {target}, Queue ID: {queue_id}")  
            
            self.master_queue.append([self.time, source, target, 'departure'])