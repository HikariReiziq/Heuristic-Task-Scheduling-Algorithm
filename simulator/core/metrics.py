"""
Metrics calculation module for Cloud Task Scheduling.
Provides mathematical formulations for Makespan, Total Cost, Resource Utilization,
Degree of Imbalance (DI), and Waiting Time.
"""

from typing import List, Dict
from core.models import TaskAllocation, VirtualMachine

def calculate_makespan(vm_ready_times: Dict[int, float]) -> float:
    """Makespan = max(ready_time_j for all VMs)."""
    if not vm_ready_times:
        return 0.0
    return max(vm_ready_times.values())


def calculate_total_cost(allocations: List[TaskAllocation]) -> float:
    """Total financial cost = sum of costs of all allocated tasks."""
    return sum(a.cost for a in allocations)


def calculate_resource_utilization(vm_ready_times: Dict[int, float], makespan: float) -> float:
    """
    Resource Utilization (RU in %) = (sum(RT_j) / (num_vms * Makespan)) * 100%
    Measures how efficiently VMs are utilized rather than remaining idle.
    """
    num_vms = len(vm_ready_times)
    if num_vms == 0 or makespan <= 0:
        return 0.0
    total_busy_time = sum(vm_ready_times.values())
    return (total_busy_time / (num_vms * makespan)) * 100.0


def calculate_degree_of_imbalance(vm_ready_times: Dict[int, float]) -> float:
    """
    Degree of Imbalance (DI) = (T_max - T_min) / T_avg
    Measures load distribution uniformity across heterogeneous VMs.
    Lower values indicate more balanced workloads.
    """
    if not vm_ready_times:
        return 0.0
    times = list(vm_ready_times.values())
    t_max = max(times)
    t_min = min(times)
    t_avg = sum(times) / len(times)
    if t_avg == 0:
        return 0.0
    return (t_max - t_min) / t_avg


def calculate_avg_waiting_time(allocations: List[TaskAllocation]) -> float:
    """Average time tasks spend waiting in the queue before execution starts."""
    if not allocations:
        return 0.0
    return sum(a.waiting_time for a in allocations) / len(allocations)
