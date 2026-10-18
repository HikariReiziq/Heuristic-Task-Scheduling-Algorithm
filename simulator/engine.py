"""
Mesin Simulasi Cloud & Broker.
Terinspirasi arsitektur CloudSim Plus / ansul2k/cloud-simulator.
Mengatur pengiriman task, kumpulan VM, dan eksekusi penjadwalan.
Dirancang untuk SOKA - Kelompok 4 (ITS 2026).
"""

from typing import List, Dict, Any, Type
import copy
from core.models import Task, VirtualMachine, SimulationResult
from schedulers.base import BaseScheduler

class CloudBroker:
    """
    Berperan sebagai DatacenterBroker / Global Scheduler di CloudSim.
    Menerima task dari Cloud Consumer lalu memetakannya ke Virtual Machine
    sesuai heuristik penjadwalan yang aktif.

    Broker tidak menyimpan daftar datacenter/host/VM sendiri; daftar VM dan task
    dikirim oleh run_simulation.py dari fungsi di benchmarks/datasets.py.
    """

    # [UBAH BROKER] Nama broker yang tampil di log trace adalah teks tetap
    # "SOKA_CloudBroker" di core/cloudsim_logger.py, bukan parameter ini.
    def __init__(self, name: str = "SOKA_CloudBroker"):
        self.name = name
        self.registered_schedulers: Dict[str, BaseScheduler] = {}

    def register_scheduler(self, scheduler: BaseScheduler) -> None:
        """Mendaftarkan algoritma penjadwalan ke broker."""
        self.registered_schedulers[scheduler.name] = scheduler

    def run_single(
        self,
        scheduler_name: str,
        tasks: List[Task],
        vms: List[VirtualMachine]
    ) -> SimulationResult:
        """Menjalankan satu scheduler pada salinan (deep copy) task dan VM."""
        if scheduler_name not in self.registered_schedulers:
            raise ValueError(f"Scheduler '{scheduler_name}' not registered in broker.")

        scheduler = self.registered_schedulers[scheduler_name]
        tasks_copy = [copy.deepcopy(t) for t in tasks]
        vms_copy = [copy.deepcopy(v) for v in vms]

        return scheduler.schedule(tasks_copy, vms_copy)

    def run_comparative_benchmark(
        self,
        tasks: List[Task],
        vms: List[VirtualMachine]
    ) -> Dict[str, SimulationResult]:
        """
        Menjalankan semua scheduler terdaftar dengan kondisi awal yang identik.
        Mengembalikan dict: nama scheduler -> SimulationResult.
        """
        results: Dict[str, SimulationResult] = {}
        for name, scheduler in self.registered_schedulers.items():
            # Salinan baru per algoritma agar ready_time VM dari algoritma sebelumnya tidak terbawa
            tasks_copy = [copy.deepcopy(t) for t in tasks]
            vms_copy = [copy.deepcopy(v) for v in vms]
            results[name] = scheduler.schedule(tasks_copy, vms_copy)
        return results
