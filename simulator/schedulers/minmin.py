"""
Min-Min Task Scheduling Algorithm.
Classic cloud heuristic benchmark.
Implemented for SOKA - Kelompok 4 (ITS 2026).
"""

import time
from typing import List
from core.models import Task, VirtualMachine, TaskAllocation, SimulationResult
from schedulers.base import BaseScheduler

class MinMinScheduler(BaseScheduler):
    """
    Min-Min Heuristic:
    1. For each unassigned task, find VM that gives minimum completion time.
    2. Among all tasks, select the task with the smallest minimum completion time.
    3. Assign selected task to that VM, update ready time, and repeat.
    """

    def __init__(self):
        super().__init__(name="Min-Min")

    def schedule(self, tasks: List[Task], vms: List[VirtualMachine]) -> SimulationResult:
        start_wall_time = time.perf_counter()

        for vm in vms:
            vm.reset()

        etc = self.compute_etc_matrix(tasks, vms)
        ecc = self.compute_ecc_matrix(tasks, vms)

        unassigned = list(range(len(tasks)))
        allocations: List[TaskAllocation] = []

        while unassigned:
            ct_dict, _ = self.compute_completion_matrices(tasks, vms, etc, ecc, unassigned)

            best_task_idx = None
            best_vm_idx = None
            min_overall_ct = float("inf")

            for t_idx in unassigned:
                ct_row = ct_dict[t_idx]
                vm_idx = min(range(len(vms)), key=lambda j: ct_row[j])
                min_ct = ct_row[vm_idx]

                if min_ct < min_overall_ct:
                    min_overall_ct = min_ct
                    best_task_idx = t_idx
                    best_vm_idx = vm_idx

            task = tasks[best_task_idx]
            vm = vms[best_vm_idx]

            exec_time = etc[best_task_idx][best_vm_idx]
            start_time = vm.ready_time
            finish_time = start_time + exec_time
            cost = ecc[best_task_idx][best_vm_idx]
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

            unassigned.remove(best_task_idx)

        duration_ms = (time.perf_counter() - start_wall_time) * 1000.0
        return self._build_result(tasks, vms, allocations, duration_ms)
