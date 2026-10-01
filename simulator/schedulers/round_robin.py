"""
Round Robin (RR) Task Scheduling Algorithm.
Standard cyclic distribution benchmark.
Implemented for SOKA - Kelompok 4 (ITS 2026).
"""

import time
from typing import List
from core.models import Task, VirtualMachine, TaskAllocation, SimulationResult
from schedulers.base import BaseScheduler

class RoundRobinScheduler(BaseScheduler):
    """
    Round Robin (RR) Scheduler:
    Assigns tasks to VMs in cyclic sequence: 0, 1, ..., M-1, 0, 1, ...
    Disregards heterogeneity and costs; serves as a baseline for dispersion.
    """

    def __init__(self):
        super().__init__(name="Round Robin (RR)")

    def schedule(self, tasks: List[Task], vms: List[VirtualMachine]) -> SimulationResult:
        start_wall_time = time.perf_counter()

        for vm in vms:
            vm.reset()

        etc = self.compute_etc_matrix(tasks, vms)
        ecc = self.compute_ecc_matrix(tasks, vms)

        allocations: List[TaskAllocation] = []
        num_vms = len(vms)

        for i, task in enumerate(tasks):
            vm_idx = i % num_vms
            vm = vms[vm_idx]

            exec_time = etc[i][vm_idx]
            start_time = vm.ready_time
            finish_time = start_time + exec_time
            cost = ecc[i][vm_idx]
            waiting_time = max(0.0, start_time - task.arrival_time)

            vm.ready_time = finish_time
            vm.ready_cost += cost
            vm.allocated_task_ids.append(task.id)

            allocations.append(TaskAllocation(
                task_id=task.id,
                task_name=task.name,
                vm_id=vm.id,
                vm_name=vm.name,
                start_time=start_time,
                execution_time=exec_time,
                finish_time=finish_time,
                cost=cost,
                waiting_time=waiting_time
            ))

        duration_ms = (time.perf_counter() - start_wall_time) * 1000.0
        return self._build_result(tasks, vms, allocations, duration_ms)
