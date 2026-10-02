"""
Execution Time based Sufferage Algorithm (ETSA).
Baseline paper: Krishnaveni H., Sinthu Janita Prakash V. (Springer AISC 2019).
Implemented for SOKA - Kelompok 4 (ITS 2026).
"""

import time
from typing import List
from core.models import Task, VirtualMachine, TaskAllocation, SimulationResult
from schedulers.base import BaseScheduler

class ETSAScheduler(BaseScheduler):
    """
    ETSA Scheduler: Focuses on Completion Time Sufferage.
    In each round:
      1. For each task, compute Sufferage = SMICT - FMICT.
      2. Pick task with maximum Sufferage value.
      3. Map to VM with minimum completion time (fastest available VM).
    """

    def __init__(self):
        super().__init__(name="ETSA (Existing Baseline)")

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
            max_sufferage = -1.0
            best_vm_idx = None

            for t_idx in unassigned:
                ct_row = ct_dict[t_idx]
                best_j = 0
                second_j = 0
                min1 = ct_row[0]
                min2 = float("inf")
                for j in range(1, len(ct_row)):
                    v = ct_row[j]
                    if v < min1:
                        min2 = min1
                        second_j = best_j
                        min1 = v
                        best_j = j
                    elif v < min2:
                        min2 = v
                        second_j = j

                sufferage = (min2 - min1) if len(ct_row) > 1 else 0.0

                if sufferage > max_sufferage:
                    max_sufferage = sufferage
                    best_task_idx = t_idx
                    best_vm_idx = best_j

            # In case of tie or zero sufferage, fallback to first task
            if best_task_idx is None:
                best_task_idx = unassigned[0]
                ct_row = ct_dict[best_task_idx]
                best_vm_idx = 0
                min_v = ct_row[0]
                for j in range(1, len(ct_row)):
                    if ct_row[j] < min_v:
                        min_v = ct_row[j]
                        best_vm_idx = j

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
                waiting_time=waiting_time,
                datacenter_id=getattr(vm, "datacenter_id", 2),
                datacenter_name=getattr(vm, "datacenter_name", "Datacenter Jakarta")
            ))

            unassigned.remove(best_task_idx)

        duration_ms = (time.perf_counter() - start_wall_time) * 1000.0
        return self._build_result(tasks, vms, allocations, duration_ms)
