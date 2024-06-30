import math

class MMckQueue:
    def __init__(self, arrival_rate, service_rate, num_servers, system_capacity):
        self.lambda_ = arrival_rate
        self.mu = service_rate
        self.c = num_servers
        self.k = system_capacity
        self.rho = self.lambda_ / (self.c * self.mu)
        self.p0 = self._calculate_p0()
        self.pn = self._calculate_pn()
        self.L = self._calculate_L()
        self.Lq = self._calculate_Lq()
        self.Ls = self.L - self.Lq
        self.lambda_eff = self.lambda_ * (1 - self.pn[self.k])
        self.W = self.L / self.lambda_eff
        self.Wq = self.Lq / self.lambda_eff
        self.Ws = 1 / self.mu

    def _calculate_p0(self):
        sum1 = sum((self.lambda_ / self.mu) ** n / math.factorial(n) for n in range(self.c))
        sum2 = ((self.lambda_ / self.mu) ** self.c / math.factorial(self.c)) * sum((self.lambda_ / (self.c * self.mu)) ** n for n in range(self.k - self.c + 1))
        return 1 / (sum1 + sum2)

    def _calculate_pn(self):
        pn = {}
        for n in range(self.k + 1):
            if n <= self.c:
                pn[n] = (self.lambda_ / self.mu) ** n * self.p0 / math.factorial(n)
            else:
                pn[n] = (self.lambda_ / self.mu) ** n * self.p0 / (self.c ** (n - self.c) * math.factorial(self.c))
        return pn

    def _calculate_L(self):
        return sum(n * self.pn[n] for n in range(self.k + 1))

    def _calculate_Lq(self):
        return sum((n - self.c) * self.pn[n] for n in range(self.c + 1, self.k + 1))

    def print_results(self):
        print(f"Utilization factor (rho): {self.rho:.4f}")
        print(f"P0: {self.p0:.4f}")
        print(f"L: {self.L:.4f}")
        print(f"Lq: {self.Lq:.4f}")
        print(f"Ls: {self.Ls:.4f}")
        print(f"λ_eff: {self.lambda_eff:.4f}")
        print(f"W: {self.W:.4f}")
        print(f"Wq: {self.Wq:.4f}")
        print(f"Ws: {self.Ws:.4f}")

# Example usage
if __name__ == "__main__":
    arrival_rate = 20  # customers per hour
    service_rate = 5  # customers per hour per server
    num_servers = 1
    system_capacity = 10

    queue = MMckQueue(arrival_rate, service_rate, num_servers, system_capacity)
    queue.print_results()



def logging(self):        
    #hande data as numpy array
    data = np.array(self.agents_data)
    departure_time = data[:,2]
    arrival_time = data[:,0]
    service_start_time = data[:,1]
    queue_length = data[:,3]
    total_time_in_system = sum(departure_time) - sum(arrival_time)
    total_time_in_service = sum(departure_time) - sum(service_start_time)
    total_customers = max(data[:,5])
    

    #simulation results
    avg_num_in_system = total_time_in_system / self.time if self.time > 0 else 0
    avg_num_in_queue = sum(queue_length)/total_customers
    avg_time_in_system = total_time_in_system / total_customers if total_customers > 0 else 0
    avg_time_in_service = total_time_in_service / total_customers if total_customers > 0 else 0
    avg_time_in_queue = avg_time_in_system - avg_time_in_service
    
    print('Simulation results:')
    print(f"Number of customer blocked : {self.blocked_customer}")
    print(f'Average number of customers in system: {avg_num_in_system:.2f}')
    print(f'Average number of customers in queue: {avg_num_in_queue:.2f}')
    print(f'Average time spent in system: {avg_time_in_system:.2f}')
    print(f'Average time spent in queue: {avg_time_in_queue:.2f}')
    print(f'Average time spent in service: {avg_time_in_service:.2f}')
    
    #theoretical results
    if self.max_queue_length == float("inf"):    
        rho = self.arrival_rate / (num_servers*self.service_rate)
        A = 0
        for a in range(0, num_servers):
            A += pow((num_servers*rho), a) / math.factorial(a)
        B = pow((num_servers * rho), num_servers) / (math.factorial(num_servers)*(1-rho)) 
        pi_0 = 1 /  (A + B)
        
        p_custo_gth_service_num = pow((num_servers*rho),num_servers)* pi_0
        p_custo_gth_service_den = (math.factorial(num_servers))*(1-rho)
        p_cust_gth_ser = p_custo_gth_service_num / p_custo_gth_service_den
        
        L_q = p_cust_gth_ser * rho / (1 - rho)
        W_q = L_q / arrival_rate
        L = L_q +  (arrival_rate/service_rate)
        W = L / arrival_rate
    
    else:
        




    print('\nTheoretical steady-state values:')
    print(f'Steady state: {pi_0}, rho: {rho}, P(cust>server) : {p_cust_gth_ser}')
    print(f'Average number of customers in system: {L:.2f}')
    print(f'Average number in queue: {L_q:.2f}')
    print(f'Average time spent in system: {W:.2f}')
    print(f'Average time spent in queue: {W_q:.2f}')
    print(f'Average time spent in service: {1 / self.service_rate:.2f}')  