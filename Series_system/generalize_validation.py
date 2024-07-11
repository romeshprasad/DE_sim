import math

class MMQueue:
    def __init__(self, arrival_rate, service_rate):
        self.lambda_ = arrival_rate
        self.mu = service_rate
        self.rho = self.lambda_ / self.mu

    def calculate_measures(self):
        pass

    def print_results(self):
        #print(f"Utilization factor (rho): {self.rho:.4f}")
        print(f"L: {self.L:.4f}")
        print(f"Lq: {self.Lq:.4f}")
        print(f"Ls: {self.Ls:.4f}")
        print(f"W: {self.W:.4f}")
        print(f"Wq: {self.Wq:.4f}")
        print(f"Ws: {self.Ws:.4f}")

class MM1Queue(MMQueue):
    def calculate_measures(self):
        self.L = self.rho / (1 - self.rho)
        self.Lq = self.rho**2 / (1 - self.rho)
        self.Ls = self.rho
        self.W = 1 / (self.mu - self.lambda_)
        self.Wq = self.rho / (self.mu - self.lambda_)
        self.Ws = 1 / self.mu

class MM1kQueue(MMQueue):
    def __init__(self, arrival_rate, service_rate, k):
        super().__init__(arrival_rate, service_rate)
        self.k = k

    def calculate_measures(self):
        if self.rho == 1:
            p0 = 1 / (self.k + 1)
        else:
            p0 = (1 - self.rho) / (1 - self.rho**(self.k + 1))
        
        self.L = self.rho * (1 - (self.k + 1) * self.rho**self.k + self.k * self.rho**(self.k + 1)) / ((1 - self.rho) * (1 - self.rho**(self.k + 1)))
        self.Lq = self.L - self.rho * (1 - p0)
        self.Ls = self.L - self.Lq
        self.lambda_eff = self.lambda_ * (1 - self.rho**self.k * p0)
        self.W = self.L / self.lambda_eff
        self.Wq = self.Lq / self.lambda_eff
        self.Ws = 1 / self.mu

class MMcQueue(MMQueue):
    def __init__(self, arrival_rate, service_rate, c):
        super().__init__(arrival_rate, service_rate)
        self.c = c
        self.rho = self.lambda_ / (self.c * self.mu)

    def calculate_measures(self):
        r = self.lambda_ / self.mu
        p0 = 1 / (sum(r**n / math.factorial(n) for n in range(self.c)) + 
                   (r**self.c / math.factorial(self.c)) * (1 / (1 - self.rho)))
        
        self.Lq = (r**self.c * self.rho * p0) / (math.factorial(self.c) * (1 - self.rho)**2)
        self.L = self.Lq + r
        self.Ls = r
        self.W = self.L / self.lambda_
        self.Wq = self.Lq / self.lambda_
        self.Ws = 1 / self.mu

class MMckQueue(MMQueue):
    def __init__(self, arrival_rate, service_rate, c, k):
        super().__init__(arrival_rate, service_rate)
        self.c = c
        self.k = k
        self.rho = self.lambda_ / (self.c * self.mu)

    def calculate_measures(self):
        if self.c == 1:
            # If c = 1, use M/M/1/k calculations
            mm1k = MM1kQueue(self.lambda_, self.mu, self.k)
            mm1k.calculate_measures()
            self.L = mm1k.L
            self.Lq = mm1k.Lq
            self.Ls = mm1k.Ls
            self.W = mm1k.W
            self.Wq = mm1k.Wq
            self.Ws = mm1k.Ws
            self.lambda_eff = mm1k.lambda_eff
        else:
            p0 = self._calculate_p0()
            pn = self._calculate_pn(p0)
            
            self.L = sum(n * pn[n] for n in range(self.k + 1))
            self.Lq = sum((n - self.c) * pn[n] for n in range(self.c + 1, self.k + 1))
            self.Ls = self.L - self.Lq
            self.lambda_eff = self.lambda_ * (1 - pn[self.k])
            self.W = self.L / self.lambda_eff
            self.Wq = self.Lq / self.lambda_eff
            self.Ws = 1 / self.mu

    def _calculate_p0(self):
        sum1 = sum((self.lambda_ / self.mu) ** n / math.factorial(n) for n in range(self.c))
        sum2 = ((self.lambda_ / self.mu) ** self.c / math.factorial(self.c)) * sum((self.lambda_ / (self.c * self.mu)) ** n for n in range(self.k - self.c + 1))
        return 1 / (sum1 + sum2)

    def _calculate_pn(self, p0):
        pn = {}
        for n in range(self.k + 1):
            if n <= self.c:
                pn[n] = (self.lambda_ / self.mu) ** n * p0 / math.factorial(n)
            else:
                pn[n] = (self.lambda_ / self.mu) ** n * p0 / (self.c ** (n - self.c) * math.factorial(self.c))
        return pn

class series():
    def __init__(self, arrival_rate, service_rate, c):
        self.lambda_ = arrival_rate
        self.mu = service_rate 
        self.c = c
        self.rho = [self.lambda_/ (self.mu[i]*self.c[i]) for i in range(len(self.mu))]
        self.data = {stages:[] for stages in range(1, len(c))}
            
    def calculate_measures(self):
        for stage in range(len(self.c)):
            if self.c[stage] == 1:
                self.L = self.rho[stage] / (1 - self.rho[stage])
                self.Lq = self.rho[stage]**2 / (1 - self.rho[stage])
                self.Ls = self.rho[stage]
                self.W = 1 / (self.mu[stage] - self.lambda_)
                self.Wq = self.rho[stage] / (self.mu[stage] - self.lambda_)
                self.Ws = 1 / self.mu[stage]
            else:
                r = self.lambda_ / self.mu[stage]
                p0 = 1 / (sum(r**n / math.factorial(n) for n in range(self.c[stage])) + 
                        (r**self.c[stage] / math.factorial(self.c[stage])) * (1 / (1 - self.rho[stage])))
                
                self.Lq = (r**self.c[stage] * self.rho[stage] * p0) / (math.factorial(self.c[stage]) * (1 - self.rho[stage])**2)
                self.L = self.Lq + r
                self.Ls = r
                self.W = self.L / self.lambda_
                self.Wq = self.Lq / self.lambda_
                self.Ws = 1 / self.mu[stage]

            self.data[stage + 1] = [self.L, self.Lq, self.Ls, self.W, self.Wq, self.Ws]
        
        return self.data
    
    def print_results(self):
        print(f"Utilization factor (rho): {self.rho}")
        print(f"L: {self.L:.4f}")
        print(f"Lq: {self.Lq:.4f}")
        print(f"Ls: {self.Ls:.4f}")
        print(f"W: {self.W:.4f}")
        print(f"Wq: {self.Wq:.4f}")
        print(f"Ws: {self.Ws:.4f}")

def analyze_queue(queue_type, *args):
    queue = queue_type(*args)
    queue.calculate_measures()
    print(f"\n{queue_type.__name__} Results:")
    queue.print_results()

# Example usage
if __name__ == "__main__":
    arrival_rate = 54  # customers per hour
    #service_rate = 6  # customers per hour
    num_servers = [1,3]
    service_rate = [60, 20]

    # analyze_queue(MM1Queue, arrival_rate, service_rate)
    # analyze_queue(MM1kQueue, arrival_rate, service_rate, 10)  # k = 10
    # analyze_queue(MMcQueue, arrival_rate, service_rate, 3)    # c = 3
    # analyze_queue(MMckQueue, arrival_rate, service_rate, 3, 10)  # c = 3, k = 10
    # analyze_queue(MMckQueue, arrival_rate, service_rate, 1, 10)  # c = 1, k = 10 (equivalent to M/M/1/k)

    x = series(arrival_rate, service_rate, num_servers)
    l = x.calculate_measures()
    print(l)

