"""
Model Data Inti Simulator Penjadwalan Tugas Cloud (padanan entitas CloudSim).
Dirancang untuk SOKA (Strategi Optimasi Komputasi Awan) - Kelompok 4 (ITS 2026).

Pemetaan ke CloudSim:
  - Task            -> Cloudlet
  - VirtualMachine  -> Vm (sekaligus menyimpan Datacenter tempat VM berada)
  - TaskAllocation  -> satu baris hasil eksekusi Cloudlet (Cloudlet Execution Record)
  - SimulationResult-> ringkasan metrik satu algoritma

Catatan: Host fisik TIDAK dimodelkan sebagai kelas di sini. Host hanya muncul
sebagai teks di log trace (lihat core/cloudsim_logger.py, tag [UBAH HOST]).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Task:
    """Merepresentasikan satu pekerjaan komputasi / Cloudlet.

    [UBAH CLOUDLET] Nilai field ini diisi oleh fungsi di benchmarks/datasets.py,
    bukan di sini. Ubah panjang MI / ukuran file di fungsi dataset skenario terkait.
    """
    id: int
    name: str
    length_mi: float        # Panjang instruksi dalam Million Instructions (MI) = CloudletLength
    file_size_mb: float     # Ukuran transfer data dalam Megabit (Mb) = input + output file
    arrival_time: float = 0.0
    priority: int = 1       # 1: Normal, 2: Tinggi (mis. IoT yang sensitif delay)
    deadline: Optional[float] = None
    etc_row: Optional[List[float]] = None  # Jika diisi, waktu eksekusi per VM diambil langsung dari sini (benchmark Maheswaran)

    def __repr__(self) -> str:
        return f"Task(id={self.id}, name='{self.name}', MI={self.length_mi}, Mb={self.file_size_mb})"


@dataclass
class VirtualMachine:
    """Merepresentasikan satu Virtual Machine / Resource.

    [UBAH VM] Spesifikasi tiap VM (MIPS, BW, tarif, RAM, core) diisi di
    benchmarks/datasets.py. Default di bawah hanya dipakai bila dataset tidak mengisinya.
    [UBAH DATACENTER] Datacenter tidak punya kelas sendiri; keanggotaan VM ke datacenter
    ditentukan oleh field datacenter_id dan datacenter_name di bawah.
    """
    id: int
    name: str
    mips: float             # Kecepatan proses dalam Million Instructions per Second
    bandwidth_mbps: float   # Bandwidth jaringan dalam Megabit per Second
    cost_per_mi: float      # Tarif per instruksi / biaya prosesor (INR / satuan mata uang)
    ram_mb: int = 2048      # Hanya untuk tampilan log, tidak memengaruhi hasil penjadwalan
    cores: int = 1          # Hanya untuk tampilan log, tidak memengaruhi hasil penjadwalan
    ready_time: float = 0.0 # Waktu saat VM kembali bebas (diperbarui scheduler)
    ready_cost: float = 0.0 # Akumulasi biaya eksekusi di VM ini (diperbarui scheduler)
    allocated_task_ids: List[int] = field(default_factory=list)
    # [UBAH DATACENTER] Default datacenter untuk VM yang tidak diberi datacenter oleh dataset.
    # ID 2 = Jakarta, 3 = Surabaya, 4 = Makassar (CloudSim memberi ID 0-1 ke entitas sistem, jadi DC mulai dari 2).
    datacenter_id: int = 2
    datacenter_name: str = "Datacenter Jakarta"

    def reset(self) -> None:
        """Mengosongkan state dinamis VM untuk simulasi baru."""
        self.ready_time = 0.0
        self.ready_cost = 0.0
        self.allocated_task_ids = []

    def __repr__(self) -> str:
        return (f"VM(id={self.id}, name='{self.name}', MIPS={self.mips}, "
                f"BW={self.bandwidth_mbps}Mbps, CostRate={self.cost_per_mi}, "
                f"DC='{self.datacenter_name}')")


@dataclass
class TaskAllocation:
    """Catatan satu task yang sudah dialokasikan ke VM tertentu (satu baris Cloudlet Execution Record)."""
    task_id: int
    task_name: str
    vm_id: int
    vm_name: str
    start_time: float
    execution_time: float
    finish_time: float
    cost: float
    waiting_time: float
    # Disalin dari VM tujuan oleh scheduler; jangan diubah di sini, ubah di dataset VM.
    datacenter_id: int = 2
    datacenter_name: str = "Datacenter Jakarta"


@dataclass
class SimulationResult:
    """Metrik kinerja lengkap dari satu kali eksekusi algoritma penjadwalan."""
    algorithm_name: str
    num_tasks: int
    num_vms: int
    makespan: float                 # Total waktu penyelesaian (detik)
    total_cost: float               # Total biaya finansial (Rs / INR)
    resource_utilization: float     # Rata-rata utilisasi VM (persen: 0-100%)
    degree_of_imbalance: float      # Derajat ketidakseimbangan beban (DI)
    avg_waiting_time: float         # Rata-rata waktu tunggu di antrean (detik)
    vm_execution_times: Dict[int, float]
    vm_costs: Dict[int, float]
    allocations: List[TaskAllocation]
    execution_duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm_name": self.algorithm_name,
            "num_tasks": self.num_tasks,
            "num_vms": self.num_vms,
            "makespan": round(self.makespan, 4),
            "total_cost": round(self.total_cost, 4),
            "resource_utilization_pct": round(self.resource_utilization, 2),
            "degree_of_imbalance": round(self.degree_of_imbalance, 4),
            "avg_waiting_time": round(self.avg_waiting_time, 4),
            "vm_execution_times": {k: round(v, 4) for k, v in self.vm_execution_times.items()},
            "vm_costs": {k: round(v, 4) for k, v in self.vm_costs.items()},
            "allocations_count": len(self.allocations),
            "engine_runtime_ms": round(self.execution_duration_ms, 3)
        }
