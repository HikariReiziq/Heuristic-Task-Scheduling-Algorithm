"""
Standard Sufferage Scheduling Algorithm.
Classic distributed/cloud heuristic benchmark (Maheswaran et al., 1999).
Implemented for SOKA - Kelompok 4 (ITS 2026).
"""

import time
from typing import List, Dict
from core.models import Task, VirtualMachine, TaskAllocation, SimulationResult
from schedulers.base import BaseScheduler

class StandardSufferageScheduler(BaseScheduler):
    """
    Standard Sufferage Heuristic:
    Assigns resources with a conflict-resolution mechanism:
    If multiple tasks compete for the same best VM, the task with the highest sufferage wins.
    """

    def __init__(self):
        super().__init__(name="Standard Sufferage")

    def schedule(self, tasks: List[Task], vms: List[VirtualMachine]) -> SimulationResult:
        start_wall_time = time.perf_counter()

        for vm in vms:
            vm.reset()

        etc = self.compute_etc_matrix(tasks, vms)
        ecc = self.compute_ecc_matrix(tasks, vms)

        num_tasks = len(tasks)
        num_vms = len(vms)
        unassigned = set(range(num_tasks))
        allocations: List[TaskAllocation] = []

        # ct[i][j] = etc[i][j] + vms[j].ready_time
        ct = [[etc[i][j] for j in range(num_vms)] for i in range(num_tasks)]

        while unassigned:
            # Map VM -> list of (t_idx, sufferage, min_ct)
            vm_proposals: Dict[int, List[tuple]] = {j: [] for j in range(num_vms)}

            for t_idx in unassigned:
                ct_row = ct[t_idx]
                best_vm = 0
                second_vm = 0
                min1 = ct_row[0]
                min2 = float("inf")
                for j in range(1, num_vms):
                    v = ct_row[j]
                    if v < min1:
                        min2 = min1
                        second_vm = best_vm
                        min1 = v
                        best_vm = j
                    elif v < min2:
                        min2 = v
                        second_vm = j

                sufferage = (min2 - min1) if num_vms > 1 else 0.0
                vm_proposals[best_vm].append((t_idx, sufferage, min1))

            assigned_in_this_round = False

            # For each VM with proposals, assign to task with maximum sufferage
            for vm_idx in range(num_vms):
                proposals = vm_proposals[vm_idx]
                if not proposals:
                    continue

                # Sort by sufferage descending; tie-breaker: minimum completion time
                proposals.sort(key=lambda x: (x[1], -x[2]), reverse=True)
                winning_task_idx, _, _ = proposals[0]

                task = tasks[winning_task_idx]
                vm = vms[vm_idx]

                exec_time = etc[winning_task_idx][vm_idx]
                start_time = vm.ready_time
                finish_time = start_time + exec_time
                cost = ecc[winning_task_idx][vm_idx]
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

                unassigned.remove(winning_task_idx)
                assigned_in_this_round = True

                # Update only the modified VM column in ct for remaining tasks
                for rem_idx in unassigned:
                    ct[rem_idx][vm_idx] = etc[rem_idx][vm_idx] + finish_time

                break  # Re-evaluate proposals after allocation

            if not assigned_in_this_round and unassigned:
                # Emergency fallback
                t_idx = unassigned[0]
                ct_row = ct_dict[t_idx]
                best_vm_idx = min(range(len(vms)), key=lambda j: ct_row[j])
                vm = vms[best_vm_idx]
                exec_time = etc[t_idx][best_vm_idx]
                start_time = vm.ready_time
                finish_time = start_time + exec_time
                cost = ecc[t_idx][best_vm_idx]

                vm.ready_time = finish_time
                vm.ready_cost += cost
                vm.allocated_task_ids.append(tasks[t_idx].id)

                allocations.append(TaskAllocation(
                    task_id=tasks[t_idx].id,
                    task_name=tasks[t_idx].name,
                    vm_id=vm.id,
                    vm_name=vm.name,
                    start_time=start_time,
                    execution_time=exec_time,
                    finish_time=finish_time,
                    cost=cost,
                    waiting_time=max(0.0, start_time - tasks[t_idx].arrival_time),
                    datacenter_id=getattr(vm, "datacenter_id", 2),
                    datacenter_name=getattr(vm, "datacenter_name", "Datacenter Jakarta")
                ))
                unassigned.remove(t_idx)

        duration_ms = (time.perf_counter() - start_wall_time) * 1000.0
        return self._build_result(tasks, vms, allocations, duration_ms)
