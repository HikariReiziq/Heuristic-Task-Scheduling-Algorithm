"""
Cost and Completion Time based Sufferage Algorithm (CCTSA).
Proposed by H. Krishnaveni, Dr. D. I. George Amalarethinam, Dr. V. Sinthu Janita (IJRECE 2019).
Implemented for SOKA - Kelompok 4 (ITS 2026).
"""

import time
from typing import List, Dict, Tuple
from core.models import Task, VirtualMachine, TaskAllocation, SimulationResult
from schedulers.base import BaseScheduler

class CCTSAScheduler(BaseScheduler):
    """
    CCTSA Heuristic Scheduler.
    Uses Dual Sufferage Values:
      - SVCT: Completion Time Sufferage (SMICT - FMICT)
      - SVC: Cost Sufferage (FMXC - SMXC)
    Selects tasks based on time/cost urgency and maps to resources balancing makespan and financial cost.
    """

    def __init__(self, time_weight: float = 0.5, cost_weight: float = 0.5):
        super().__init__(name="CCTSA (Proposed)")
        self.w_time = time_weight
        self.w_cost = cost_weight

    def schedule(self, tasks: List[Task], vms: List[VirtualMachine]) -> SimulationResult:
        start_wall_time = time.perf_counter()

        # Reset VM dynamic state
        for vm in vms:
            vm.reset()

        etc = self.compute_etc_matrix(tasks, vms)
        ecc = self.compute_ecc_matrix(tasks, vms)

        unassigned = list(range(len(tasks)))
        allocations: List[TaskAllocation] = []

        while unassigned:
            ct_dict, cc_dict = self.compute_completion_matrices(tasks, vms, etc, ecc, unassigned)

            task_metrics: Dict[int, Dict[str, float]] = {}

            for t_idx in unassigned:
                ct_row = ct_dict[t_idx]
                cc_row = cc_dict[t_idx]

                # Completion Time: First and Second Minimum
                sorted_ct = sorted(ct_row)
                fmict = sorted_ct[0]
                smict = sorted_ct[1] if len(sorted_ct) > 1 else fmict
                svct = smict - fmict

                # Completion Cost: First and Second Maximum
                sorted_cc = sorted(cc_row, reverse=True)
                fmxc = sorted_cc[0]
                smxc = sorted_cc[1] if len(sorted_cc) > 1 else fmxc
                svc = fmxc - smxc

                task_metrics[t_idx] = {
                    "FMICT": fmict,
                    "SMICT": smict,
                    "SVCT": svct,
                    "FMXC": fmxc,
                    "SMXC": smxc,
                    "SVC": svc
                }

            # Task Selection according to Paper Pseudo-code:
            # For i = Unassigned_Task_Count to 0 (backward scan)
            chosen_task_idx = None

            for t_idx in reversed(unassigned):
                m = task_metrics[t_idx]
                if m["SVCT"] > m["FMICT"] and m["SVC"] < m["FMXC"]:
                    chosen_task_idx = t_idx
                    break

            # Fallback Rule: if no task strictly satisfies both criteria,
            # select the task with the highest combined sufferage impact
            if chosen_task_idx is None:
                # Maximize normalized time sufferage + cost sufferage
                def sufferage_score(idx: int) -> float:
                    m = task_metrics[idx]
                    norm_svct = m["SVCT"] / (m["FMICT"] + 1e-9)
                    norm_svc = m["SVC"] / (m["FMXC"] + 1e-9)
                    return norm_svct + norm_svc

                chosen_task_idx = max(unassigned, key=sufferage_score)

            # Resource Selection:
            # Paper line 19: Assign Ch_Task to resource j that gives the minimum completion time and cost
            ct_row = ct_dict[chosen_task_idx]
            cc_row = cc_dict[chosen_task_idx]

            max_ct = max(ct_row) if max(ct_row) > 0 else 1.0
            max_cc = max(cc_row) if max(cc_row) > 0 else 1.0

            best_vm_idx = None
            best_score = float("inf")

            for j in range(len(vms)):
                norm_ct = ct_row[j] / max_ct
                norm_cc = cc_row[j] / max_cc
                score = (self.w_time * norm_ct) + (self.w_cost * norm_cc)

                if score < best_score:
                    best_score = score
                    best_vm_idx = j

            # Allocate chosen task to best VM
            task = tasks[chosen_task_idx]
            vm = vms[best_vm_idx]

            exec_time = etc[chosen_task_idx][best_vm_idx]
            start_time = vm.ready_time
            finish_time = start_time + exec_time
            cost = ecc[chosen_task_idx][best_vm_idx]
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

            unassigned.remove(chosen_task_idx)

        duration_ms = (time.perf_counter() - start_wall_time) * 1000.0
        return self._build_result(tasks, vms, allocations, duration_ms)
