"""
Base Scheduler Interface and Common Utilities for Cloud Task Scheduling.
Designed for SOKA - Kelompok 4 (ITS 2026).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
import time

from core.models import Task, VirtualMachine, TaskAllocation, SimulationResult
from core.metrics import (
    calculate_makespan,
    calculate_total_cost,
    calculate_resource_utilization,
    calculate_degree_of_imbalance,
    calculate_avg_waiting_time
)

class BaseScheduler(ABC):
    """Abstract base class for all cloud scheduling policies."""

    def __init__(self, name: str):
        self.name = name

    @staticmethod
    def compute_etc_matrix(tasks: List[Task], vms: List[VirtualMachine]) -> List[List[float]]:
        """
        Expected Time to Compute (ETC) Matrix:
        If task.etc_row is provided (e.g. Maheswaran benchmark), use it directly.
        Otherwise: ET_ij = (MI_i / MIPS_j) + (Mb_i / Mbps_j) [Equation 2 from paper]
        """
        matrix = []
        for task in tasks:
            if task.etc_row is not None and len(task.etc_row) == len(vms):
                matrix.append(list(task.etc_row))
            else:
                row = []
                for vm in vms:
                    exec_time = (task.length_mi / vm.mips) + (task.file_size_mb / vm.bandwidth_mbps)
                    row.append(exec_time)
                matrix.append(row)
        return matrix

    @staticmethod
    def compute_ecc_matrix(tasks: List[Task], vms: List[VirtualMachine]) -> List[List[float]]:
        """
        Expected Cost to Compute (ECC) Matrix:
        Cost_ij = MI_i * Cost of processor_j (INR) [Equation 3 from paper]
        """
        matrix = []
        for task in tasks:
            row = []
            for vm in vms:
                cost = task.length_mi * vm.cost_per_mi
                row.append(cost)
            matrix.append(row)
        return matrix

    @staticmethod
    def compute_completion_matrices(
        tasks: List[Task],
        vms: List[VirtualMachine],
        etc: List[List[float]],
        ecc: List[List[float]],
        unassigned_indices: List[int]
    ) -> Tuple[Dict[int, List[float]], Dict[int, List[float]]]:
        """
        Computes dynamic Completion Time and Completion Cost matrices for unassigned tasks:
        Completion Time_ij = ET_ij + ReadyTime_j
        Completion Cost_ij = Cost_ij + ReadyCost_j [Equation 1 from paper]
        """
        ct_dict = {}
        cc_dict = {}
        for t_idx in unassigned_indices:
            ct_row = [etc[t_idx][j] + vms[j].ready_time for j in range(len(vms))]
            cc_row = [ecc[t_idx][j] + vms[j].ready_cost for j in range(len(vms))]
            ct_dict[t_idx] = ct_row
            cc_dict[t_idx] = cc_row
        return ct_dict, cc_dict

    @abstractmethod
    def schedule(self, tasks: List[Task], vms: List[VirtualMachine]) -> SimulationResult:
        """Execute the scheduling heuristic and return full simulation results."""
        pass

    def _build_result(
        self,
        tasks: List[Task],
        vms: List[VirtualMachine],
        allocations: List[TaskAllocation],
        runtime_ms: float
    ) -> SimulationResult:
        """Helper to construct a standardized SimulationResult object."""
        vm_ready_times = {vm.id: vm.ready_time for vm in vms}
        vm_costs = {vm.id: vm.ready_cost for vm in vms}
        makespan = calculate_makespan(vm_ready_times)
        total_cost = calculate_total_cost(allocations)
        ru = calculate_resource_utilization(vm_ready_times, makespan)
        di = calculate_degree_of_imbalance(vm_ready_times)
        avg_wait = calculate_avg_waiting_time(allocations)

        return SimulationResult(
            algorithm_name=self.name,
            num_tasks=len(tasks),
            num_vms=len(vms),
            makespan=makespan,
            total_cost=total_cost,
            resource_utilization=ru,
            degree_of_imbalance=di,
            avg_waiting_time=avg_wait,
            vm_execution_times=vm_ready_times,
            vm_costs=vm_costs,
            allocations=allocations,
            execution_duration_ms=runtime_ms
        )
