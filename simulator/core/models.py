"""
Core Data Models for Cloud Task Scheduling Simulator.
Designed for SOKA (Strategi Optimasi Komputasi Awan) - Kelompok 4 (ITS 2026).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Task:
    """Represents a computational job / Cloudlet."""
    id: int
    name: str
    length_mi: float        # Instruction count in Million Instructions (MI)
    file_size_mb: float     # Data transfer size in Megabits (Mb)
    arrival_time: float = 0.0
    priority: int = 1       # 1: Normal, 2: High (e.g. delay-sensitive IoT)
    deadline: Optional[float] = None
    etc_row: Optional[List[float]] = None

    def __repr__(self) -> str:
        return f"Task(id={self.id}, name='{self.name}', MI={self.length_mi}, Mb={self.file_size_mb})"


@dataclass
class VirtualMachine:
    """Represents a Virtual Machine / Resource."""
    id: int
    name: str
    mips: float             # Processing speed in Million Instructions per Second
    bandwidth_mbps: float   # Network bandwidth in Megabits per Second
    cost_per_mi: float      # Cost per instruction / processor cost (INR / currency unit)
    ram_mb: int = 2048
    cores: int = 1
    ready_time: float = 0.0 # Time when the VM becomes available
    ready_cost: float = 0.0 # Accumulated execution cost on this VM
    allocated_task_ids: List[int] = field(default_factory=list)
    datacenter_id: int = 2
    datacenter_name: str = "Datacenter Jakarta"

    def reset(self) -> None:
        """Reset dynamic state of the VM for a new simulation run."""
        self.ready_time = 0.0
        self.ready_cost = 0.0
        self.allocated_task_ids = []

    def __repr__(self) -> str:
        return (f"VM(id={self.id}, name='{self.name}', MIPS={self.mips}, "
                f"BW={self.bandwidth_mbps}Mbps, CostRate={self.cost_per_mi}, "
                f"DC='{self.datacenter_name}')")


@dataclass
class TaskAllocation:
    """Record of an allocated task on a specific VM."""
    task_id: int
    task_name: str
    vm_id: int
    vm_name: str
    start_time: float
    execution_time: float
    finish_time: float
    cost: float
    waiting_time: float
    datacenter_id: int = 2
    datacenter_name: str = "Datacenter Jakarta"


@dataclass
class SimulationResult:
    """Comprehensive performance metrics of a scheduling algorithm run."""
    algorithm_name: str
    num_tasks: int
    num_vms: int
    makespan: float                 # Total completion time (seconds)
    total_cost: float               # Total financial cost (Rs / INR)
    resource_utilization: float     # Average VM utilization (percentage: 0-100%)
    degree_of_imbalance: float      # Degree of workload imbalance (DI)
    avg_waiting_time: float         # Average queue waiting time (seconds)
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
