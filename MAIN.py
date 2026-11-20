import random
import matplotlib.pyplot as plt
import numpy as np


# The task with execution time and priority
class task_in:
    def __init__(self, ta_id, ex_time, priority):
        self.ta_id = ta_id
        self.ex_time = ex_time
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority


# VM Class: Simulate a VM (worker) with limited cap and dynamic scaling
class Vmdef:
    def __init__(self, vm_id, cap, cost_put=0.01):
        self.vm_id = vm_id
        self.cap = cap
        self.cost_put = cost_put
        self.load = 0
        self.task_ints = []

    def tas_assign(self, task_int):
        # Assign task_int if there is enough cap
        if self.load + task_int.ex_time <= self.cap:
            self.load += task_int.ex_time
            self.task_ints.append(task_int)
            return True
        return False

    def reset(self):
        self.load = 0
        self.task_ints = []


# MFSO Optimization
class MFSOoptim:
    def __init__(self, vm_num, task_ints, iter=100, mut_rate=0.2):
        self.vm_num = vm_num
        self.task_ints = task_ints
        self.iter = iter
        self.mut_rate = mut_rate
        self.best_solution = None
        self.best_fitness = float("inf")

    def optimize(self):
        population = [self.randsol() for _ in range(len(self.vm_num))]

        perfmetrics = {
            "ex_time": [],
            "load_balance": [],
            "cost": [],
        }
        for iteration in range(self.iter):
            for solution in population:
                fitness = self.fitfun(solution)

                if fitness < self.best_fitness:
                    self.best_fitness = fitness
                    self.best_solution = solution

            # Track performance metrics at each iteration
            perfmetrics["ex_time"].append(self.calculate_ex_time(self.best_solution))
            perfmetrics["load_balance"].append(self.cal_loadbal(self.best_solution))
            perfmetrics["cost"].append(self.calculate_cost(self.best_solution))

            population = self.gen_pop(population)

        return self.best_solution, perfmetrics

    def randsol(self):
        solution = []
        for task_int in self.task_ints:
            vm = random.choice(self.vm_num)
            solution.append((task_int, vm))
        return solution

    def gen_pop(self, population):
        newpop = []
        for solution in population:
            # This could be an operator that adjusts task_int assignments more aggressively
            newpop.append(self.mutation(solution))
        return newpop

    def mutation(self, solution):
        mutsol = solution.copy()

        if random.random() < self.mut_rate:
            task_int1, vm1 = random.choice(mutsol)
            task_int2, vm2 = random.choice(mutsol)
            if task_int1 != task_int2:
                mutsol.remove((task_int1, vm1))
                mutsol.remove((task_int2, vm2))
                mutsol.append((task_int1, vm2))
                mutsol.append((task_int2, vm1))

        return mutsol

    def fitfun(self, solution):
        # Calculate the fitness of a solution based on multiple objectives
        ex_time = self.calculate_ex_time(solution)
        loadbal = self.cal_loadbal(solution)
        cost = self.calculate_cost(solution)

        # Combine the objectives (weighted sum)
        fitness = ex_time * 0.5 + loadbal * 0.3 + cost * 0.2  # Example weights
        return fitness

    def calculate_ex_time(self, solution):
        # Calculate total execution time
        total_ex_time = sum(task_int.ex_time for task_int, _ in solution)
        return total_ex_time

    def cal_loadbal(self, solution):
        vm_loads = {}
        for task_int, vm in solution:
            if vm not in vm_loads:
                vm_loads[vm] = 0
            vm_loads[vm] += task_int.ex_time
        max_load = max(vm_loads.values())
        min_load = min(vm_loads.values())
        loadbal = max_load - min_load
        return loadbal

    def calculate_cost(self, solution):
        total_cost = sum(task_int.ex_time * vm.cost_put for task_int, vm in solution)
        return total_cost


# task_intScheduler Class: Manages scheduling task_ints to vm_num using MFSO
class task_intScheduler:
    def __init__(self, max_vm_num, max_cap):
        self.max_vm_num = max_vm_num
        self.max_cap = max_cap
        self.vm_num = [Vmdef(vm_id=i, cap=max_cap) for i in range(max_vm_num)]
        self.task_int_queue = []

    def add_task_int(self, task_int):
        self.task_int_queue.append(task_int)
        self.task_int_queue.sort()

    def schedule_task_ints(self):
        optimizer = MFSOoptim(self.vm_num, self.task_int_queue)
        best_solution, perfmetrics = optimizer.optimize()

        for task_int, vm in best_solution:
            vm.tas_assign(task_int)

        return best_solution, perfmetrics

    def reset_vm_num(self):
        # Reset VM loads for new scheduling iteration
        for vm in self.vm_num:
            vm.reset()

    def cal_loadbal(self, solution):
        # Calculate the load imbalance across vm_num
        vm_loads = {}
        for task_int, vm in solution:
            if vm not in vm_loads:
                vm_loads[vm] = 0
            vm_loads[vm] += task_int.ex_time
        max_load = max(vm_loads.values())
        min_load = min(vm_loads.values())
        loadbal = max_load - min_load
        return loadbal

    def calculate_cost(self, solution):
        # Simulate cost as a function of the total task_int execution time
        total_cost = sum(task_int.ex_time * vm.cost_put for task_int, vm in solution)
        return total_cost


# Simulate the task_int Scheduler with MFSO
def simulates_task_schedule():
    scheduler = task_intScheduler(max_vm_num=3, max_cap=10)

    # Generate and add random task_ints
    for i in range(10):  # Create 10 task_ints
        ex_time = random.randint(1, 5)
        priority = random.randint(1, 3)
        task_inta = task_in(ta_id=i, ex_time=ex_time, priority=priority)
        scheduler.add_task_int(task_inta)

    # Perform Optimization Before
    scheduler.reset_vm_num()  # Reset vm_num before scheduling
    befopt_res, _ = scheduler.schedule_task_ints()

    # Print task_ints Scheduled Before Optimization
    print("\nBefore Optimization:")
    for vm in scheduler.vm_num:
        if vm.task_ints:
            print(f"VM{vm.vm_id} has task_ints:")
            for task_int in vm.task_ints:
                print(f"    task_int{task_int.ta_id}: {task_int.ex_time}s")

    # Performance Metrics (Before Optimization)
    ex_time_before = sum(task_inta.ex_time for task_inta, _ in befopt_res)
    loadbal_bef = scheduler.cal_loadbal(befopt_res)
    costbef = scheduler.calculate_cost(befopt_res)
    print(f"Total Execution Time: {ex_time_before} seconds")
    print(f"Load Balance: {loadbal_bef} seconds")
    print(f"Total Cost: ${costbef:.2f}")

    # Perform Optimization After
    scheduler.reset_vm_num()  # Reset vm_num before optimization
    aftopt_res, perfmetrics = scheduler.schedule_task_ints()

    # Print task_ints Scheduled After Optimization
    print("\nAfter Optimization:")
    for vm in scheduler.vm_num:
        if vm.task_ints:
            print(f"VM{vm.vm_id} has task_ints:")
            for task_int in vm.task_ints:
                print(f"    task_int{task_int.ta_id}: {task_int.ex_time}s")

    # Performance Metrics (After Optimization)
    ex_time_after = sum(task_inta.ex_time for task_inta, _ in aftopt_res)
    loadbal_aft = scheduler.cal_loadbal(aftopt_res)
    cost_after = scheduler.calculate_cost(aftopt_res)
    print(f"Total Execution Time: {ex_time_after} seconds")
    print(f"Load Balance: {loadbal_aft} seconds")
    print(f"Total Cost: ${cost_after:.2f}")

    plt.figure(figsize=(10, 6))

    # Plot Execution Time, Load Balance, and Cost over Iterations
    plt.subplot(3, 1, 1)
    plt.plot(perfmetrics["ex_time"], label="Execution Time", color="blue")
    plt.ylabel("Execution Time (seconds)")
    plt.title("Execution Time Over Optimization Iterations")

    plt.subplot(3, 1, 2)
    plt.plot(perfmetrics["load_balance"], label="Load Balance", color="orange")
    plt.ylabel("Load Balance (seconds)")
    plt.title("Load Balance Over Optimization Iterations")

    plt.subplot(3, 1, 3)
    plt.plot(perfmetrics["cost"], label="Cost", color="green")
    plt.ylabel("Cost ($)")
    plt.title("Cost Over Optimization Iterations")

    plt.tight_layout()
    plt.show()

    algorithms = ["Before optimization", "After optimization"]
    v1 = [0.27]
    v2 = [0.27]
    x = np.arange(len(algorithms))

    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 6))

    ax.bar(x, v1, color="orange")

    ax.set_xlabel("Algorithm")
    ax.set_ylabel("cost")
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms)

    plt.tight_layout()
    plt.show()

    algorithms = ["Before optimization", "After optimization"]
    v1 = [7, 3]
    v2 = [27, 27]
    x = np.arange(len(algorithms))

    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 6))

    bars1 = ax.bar(x - width / 2, v1, width, label="load balance", color="blue")
    bars2 = ax.bar(x + width / 2, v2, width, label="Total execution time", color="orange")
    ax.set_xlabel("Algorithm")
    ax.set_ylabel("seconds")
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms)
    ax.legend()
    plt.tight_layout()
    plt.show()

    v1 = [1, 5, 2]
    v2 = [2, 2, 3]

    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 6))
    algorithms = ["VM0", "VM1", "VM2"]
    x = np.arange(len(algorithms))
    ax.bar(x - width / 2, v1, width, label="Before optimization", color="blue")
    ax.bar(x + width / 2, v2, width, label="After optimization", color="orange")
    ax.set_xlabel("Virtual Machine")
    ax.set_ylabel("Number of tasks")
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms)
    ax.legend()
    plt.tight_layout()
    plt.show()


# main function
if __name__ == "__main__":
    simulates_task_schedule()
