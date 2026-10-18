"""
Modul perhitungan metrik penjadwalan tugas cloud.
Berisi rumus Makespan, Total Biaya, Utilisasi Sumber Daya,
Degree of Imbalance (DI), dan Waktu Tunggu.
"""

from typing import List, Dict
from core.models import TaskAllocation, VirtualMachine

def calculate_makespan(vm_ready_times: Dict[int, float]) -> float:
    """Makespan = max(ready_time_j untuk semua VM)."""
    if not vm_ready_times:
        return 0.0
    return max(vm_ready_times.values())


def calculate_total_cost(allocations: List[TaskAllocation]) -> float:
    """Total biaya finansial = jumlah biaya seluruh task yang dialokasikan."""
    return sum(a.cost for a in allocations)


def calculate_resource_utilization(vm_ready_times: Dict[int, float], makespan: float) -> float:
    """
    Utilisasi Sumber Daya (RU dalam %) = (sum(RT_j) / (jumlah_vm * Makespan)) * 100%
    Mengukur seberapa efisien VM dipakai dibanding menganggur.
    """
    num_vms = len(vm_ready_times)
    if num_vms == 0 or makespan <= 0:
        return 0.0
    total_busy_time = sum(vm_ready_times.values())
    return (total_busy_time / (num_vms * makespan)) * 100.0


def calculate_degree_of_imbalance(vm_ready_times: Dict[int, float]) -> float:
    """
    Degree of Imbalance (DI) = (T_max - T_min) / T_avg
    Mengukur keseragaman distribusi beban di antara VM heterogen.
    Nilai lebih kecil berarti beban lebih seimbang.
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
    """Rata-rata waktu yang dihabiskan task menunggu di antrean sebelum dieksekusi."""
    if not allocations:
        return 0.0
    return sum(a.waiting_time for a in allocations) / len(allocations)
