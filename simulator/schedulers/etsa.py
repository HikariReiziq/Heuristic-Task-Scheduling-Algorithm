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
                sorted_indices = sorted(range(len(ct_row)), key=lambda j: ct_row[j])
                fmict_vm = sorted_indices[0]
                fmict = ct_row[fmict_vm]
                smict = ct_row[sorted_indices[1]] if len(sorted_indices) > 1 else fmict
                sufferage = smict - fmict

                if sufferage > max_sufferage:
                    max_sufferage = sufferage
                    best_task_idx = t_idx
                    best_vm_idx = fmict_vm

            # In case of tie or zero sufferage, fallback to first task
            if best_task_idx is None:
                best_task_idx = unassigned[0]
                ct_row = ct_dict[best_task_idx]
                best_vm_idx = min(range(len(vms)), key=lambda j: ct_row[j])

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
