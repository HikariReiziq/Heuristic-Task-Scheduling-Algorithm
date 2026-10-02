"""
Benchmark Datasets for Cloud Task Scheduling.
SOKA (Strategi Optimasi Komputasi Awan) - Kelompok 4 (ITS 2026).

Includes:
1. Exact Table I and Table II from paper Krishnaveni dkk. (IJRECE 2019).
2. Reference validation targets from Tables III, IV, V, VI.
3. Scalability workload generator for 25, 50, 75, 100, 150, 200 tasks across 5-14 VMs.
4. Google Cloud Jobs (GoCJ) real-world dataset generator (1.000 tasks: Small, Med, Large, XL).
5. Tugas 2A / 2B Cloudlet Benchmark (1.000 tasks @ 50.000 MI, 300 MB input, 100 MB output).
6. Maheswaran et al. (JPDC 1999) 16-quadrant ETC matrix benchmark (Inconsistent HiHi, etc.).
"""

import random
from typing import List, Dict, Any, Tuple
from core.models import Task, VirtualMachine

# ============================================================================
# 1. Paper Krishnaveni (2019) Base Datasets (Table I & II)
# ============================================================================

def get_paper_table1_vms() -> List[VirtualMachine]:
    """
    Table I: Specification of the Resources (from paper):
    R1: 50 MIPS, 100 Mbps, Cost: 0.03 INR
    R2: 100 MIPS, 200 Mbps, Cost: 0.12 INR
    R3: 200 MIPS, 250 Mbps, Cost: 0.24 INR
    """
    return [
        VirtualMachine(id=1, name="R1", mips=50.0, bandwidth_mbps=100.0, cost_per_mi=0.03),
        VirtualMachine(id=2, name="R2", mips=100.0, bandwidth_mbps=200.0, cost_per_mi=0.12),
        VirtualMachine(id=3, name="R3", mips=200.0, bandwidth_mbps=250.0, cost_per_mi=0.24),
    ]


def get_paper_table2_tasks() -> List[Task]:
    """
    Table II: Specification of the Tasks (from paper):
    T1: 206 MI, 44 Mb
    T2: 50 MI, 95 Mb
    T3: 128 MI, 64 Mb
    T4: 69 MI, 30 Mb
    T5: 118 MI, 59 Mb
    T6: 112 MI, 47 Mb
    T7: 21 MI, 39 Mb
    T8: 200 MI, 61 Mb
    T9: 90 MI, 23 Mb
    T10: 45 MI, 23 Mb
    """
    specs = [
        (1, 206.0, 44.0),
        (2, 50.0, 95.0),
        (3, 128.0, 64.0),
        (4, 69.0, 30.0),
        (5, 118.0, 59.0),
        (6, 112.0, 47.0),
        (7, 21.0, 39.0),
        (8, 200.0, 61.0),
        (9, 90.0, 23.0),
        (10, 45.0, 23.0)
    ]
    return [Task(id=tid, name=f"T{tid}", length_mi=mi, file_size_mb=mb) for tid, mi, mb in specs]


def get_paper_reference_results() -> Dict[str, Any]:
    """Published results from Krishnaveni et al. (IJRECE 2019) for verification."""
    return {
        "table3_base": {
            "CCTSA": {
                "makespan": 4.172,
                "total_cost": 21.30,
                "resource_utilization": 91.40
            },
            "ETSA": {
                "makespan": 3.915,
                "total_cost": 25.76,
                "resource_utilization": 88.98
            }
        },
        "scalability": {
            25: {"resources": 5, "cctsa_ms": 10.23, "etsa_ms": 8.90, "cctsa_cost": 30.1, "etsa_cost": 33.3, "cctsa_ru": 90.01, "etsa_ru": 87.00},
            50: {"resources": 7, "cctsa_ms": 27.51, "etsa_ms": 22.40, "cctsa_cost": 54.7, "etsa_cost": 59.5, "cctsa_ru": 91.40, "etsa_ru": 88.20},
            75: {"resources": 8, "cctsa_ms": 48.30, "etsa_ms": 46.10, "cctsa_cost": 82.5, "etsa_cost": 93.9, "cctsa_ru": 90.50, "etsa_ru": 86.92},
            100: {"resources": 10, "cctsa_ms": 74.50, "etsa_ms": 67.90, "cctsa_cost": 111.6, "etsa_cost": 123.0, "cctsa_ru": 90.00, "etsa_ru": 86.70},
            150: {"resources": 12, "cctsa_ms": 122.40, "etsa_ms": 113.70, "cctsa_cost": 143.4, "etsa_cost": 162.8, "cctsa_ru": 89.21, "etsa_ru": 86.50},
            200: {"resources": 14, "cctsa_ms": 153.80, "etsa_ms": 137.80, "cctsa_cost": 171.2, "etsa_cost": 190.6, "cctsa_ru": 89.05, "etsa_ru": 85.11}
        }
    }


def generate_heterogeneous_vms(count: int) -> List[VirtualMachine]:
    """
    Generates a pool of heterogeneous VMs scaling from 5 to 14 VMs (Tables IV-VI).
    """
    base_templates = [
        {"name": "R1_Micro", "mips": 50.0, "bw": 100.0, "cost": 0.03},
        {"name": "R2_Small", "mips": 100.0, "bw": 200.0, "cost": 0.12},
        {"name": "R3_Medium", "mips": 200.0, "bw": 250.0, "cost": 0.24},
        {"name": "R4_Large", "mips": 300.0, "bw": 300.0, "cost": 0.35},
        {"name": "R5_XLarge", "mips": 400.0, "bw": 400.0, "cost": 0.45},
        {"name": "R6_2XLarge", "mips": 500.0, "bw": 500.0, "cost": 0.55},
        {"name": "R7_ComputeOpt", "mips": 600.0, "bw": 600.0, "cost": 0.65},
    ]

    vms: List[VirtualMachine] = []
    for i in range(count):
        template = base_templates[i % len(base_templates)]
        vms.append(VirtualMachine(
            id=i + 1,
            name=f"VM{i+1}_{template['name']}",
            mips=template["mips"] * (1.0 + (i // len(base_templates)) * 0.1),
            bandwidth_mbps=template["bw"],
            cost_per_mi=template["cost"]
        ))
    return vms


def generate_synthetic_workload(
    num_tasks: int,
    seed: int = 42,
    mean_mi: float = 110.0,
    mean_mb: float = 50.0
) -> List[Task]:
    """
    Generates synthetic cloud task workload mimicking the paper's distribution.
    Uses Poisson arrival and bounded normal distributions for MI and Mb.
    """
    rng = random.Random(seed)
    tasks: List[Task] = []
    current_time = 0.0

    for i in range(num_tasks):
        inter_arrival = rng.expovariate(1.0 / 0.5)
        current_time += inter_arrival

        mi = max(20.0, min(300.0, rng.gauss(mean_mi, 45.0)))
        mb = max(20.0, min(120.0, rng.gauss(mean_mb, 20.0)))
        priority = 2 if (i % 5 == 0) else 1

        tasks.append(Task(
            id=i + 1,
            name=f"Task_{i+1}",
            length_mi=round(mi, 1),
            file_size_mb=round(mb, 1),
            arrival_time=round(current_time, 3),
            priority=priority
        ))

    return tasks


# ============================================================================
# 2. Google Cloud Jobs (GoCJ) Real-World Workload Generator (Tugas 2B & 3)
# ============================================================================

def get_gocj_workload(num_tasks: int = 1000, seed: int = 42) -> List[Task]:
    """
    Models real-world Google Cloud Jobs (GoCJ) workload distribution.
    Job categorization based on Silvia & Moreno (2018):
      - Small (S)       : 10,000 - 50,000 MI   (30% probability)
      - Medium (M)      : 50,000 - 150,000 MI  (40% probability)
      - Large (L)       : 150,000 - 300,000 MI (20% probability)
      - Extra-Large (XL): 300,000 - 500,000 MI (10% probability)
    Data transfer sizes (file input/output) range from 100 MB to 1000 MB.
    Arrival timestamps follow a Poisson process (arrival rate lambda = 2.0 jobs/s).
    """
    rng = random.Random(seed)
    tasks: List[Task] = []
    current_time = 0.0

    for i in range(num_tasks):
        # Poisson process inter-arrival
        inter_arrival = rng.expovariate(2.0)
        current_time += inter_arrival

        p = rng.random()
        if p < 0.30:
            # Small Task
            mi = rng.uniform(10_000.0, 50_000.0)
            mb = rng.uniform(100.0, 250.0)
            tag = "S"
        elif p < 0.70:
            # Medium Task
            mi = rng.uniform(50_000.0, 150_000.0)
            mb = rng.uniform(250.0, 500.0)
            tag = "M"
        elif p < 0.90:
            # Large Task
            mi = rng.uniform(150_000.0, 300_000.0)
            mb = rng.uniform(500.0, 800.0)
            tag = "L"
        else:
            # Extra-Large Task
            mi = rng.uniform(300_000.0, 500_000.0)
            mb = rng.uniform(800.0, 1000.0)
            tag = "XL"

        tasks.append(Task(
            id=i + 1,
            name=f"GoCJ_{tag}_{i+1}",
            length_mi=round(mi, 1),
            file_size_mb=round(mb, 1),
            arrival_time=round(current_time, 4),
            priority=2 if tag in ["L", "XL"] else 1
        ))

    return tasks


def generate_gocj_vms(num_vms: int = 50) -> List[VirtualMachine]:
    """
    Generates a cloud datacenter cluster suitable for executing GoCJ workloads.
    MIPS spans from 2,000 to 20,000 MIPS across 4 tiers (Standard, Compute, Memory, High-CPU).
    """
    tiers = [
        {"name": "Standard_VM", "mips": 2500.0, "bw": 1000.0, "cost": 0.05},
        {"name": "Compute_Opt", "mips": 5000.0, "bw": 2500.0, "cost": 0.12},
        {"name": "Memory_Opt", "mips": 8000.0, "bw": 5000.0, "cost": 0.22},
        {"name": "High_CPU_Opt", "mips": 15000.0, "bw": 10000.0, "cost": 0.40},
    ]

    vms: List[VirtualMachine] = []
    for i in range(num_vms):
        template = tiers[i % len(tiers)]
        multiplier = 1.0 + (i // len(tiers)) * 0.05
        vms.append(VirtualMachine(
            id=i + 1,
            name=f"GCE_VM{i+1}_{template['name']}",
            mips=round(template["mips"] * multiplier, 1),
            bandwidth_mbps=template["bw"],
            cost_per_mi=template["cost"]
        ))
    return vms


# ============================================================================
# 3. Tugas 2A / 2B Cloudlet Benchmark (1.000 Tasks @ 50.000 MI, 400 MB)
# ============================================================================

def get_tugas2a_workload(num_tasks: int = 1000, seed: int = 42) -> List[Task]:
    """
    Workload specifications directly from SOKA Tugas 2A / Tugas 2B (Slide 11-13):
      - 1.000 Cloudlet Tasks
      - Task Length: 50.000 MI (Million Instructions)
      - Input File Size: 300 MB
      - Output File Size: 100 MB (Total network data: 400 MB)
      - Poisson Process arrival.
    """
    rng = random.Random(seed)
    tasks: List[Task] = []
    current_time = 0.0

    for i in range(num_tasks):
        inter_arrival = rng.expovariate(1.5)
        current_time += inter_arrival

        tasks.append(Task(
            id=i + 1,
            name=f"Cloudlet_Tugas2A_{i+1}",
            length_mi=50_000.0,
            file_size_mb=400.0,  # 300 MB input + 100 MB output
            arrival_time=round(current_time, 4),
            priority=1
        ))

    return tasks


def get_tugas2a_vms(num_vms: int = 50) -> List[VirtualMachine]:
    """
    Infrastruktur VM Heterogen Tugas 2A / 2B:
    Berasal dari arsitektur 2 Datacenter, 20 Host (16-core, 64 GB RAM),
    1.000 VM (50 VM/host, 4 vCPU, 8 GB RAM) dengan Resource Over-commitment.
    MIPS disesuaikan secara heterogen antara 1.000 MIPS s.d. 8.000 MIPS.
    """
    tiers = [
        {"name": "Standard_Host1", "mips": 1500.0, "bw": 1000.0, "cost": 0.04},
        {"name": "Medium_Host2", "mips": 3000.0, "bw": 2500.0, "cost": 0.10},
        {"name": "Large_Host3", "mips": 5000.0, "bw": 5000.0, "cost": 0.18},
        {"name": "Ultra_Host4", "mips": 8000.0, "bw": 10000.0, "cost": 0.32},
    ]

    vms: List[VirtualMachine] = []
    half = num_vms // 2
    for i in range(num_vms):
        t = tiers[i % len(tiers)]
        multiplier = 1.0 + (i // len(tiers)) * 0.05
        dc_id = 2 if i < half else 3
        dc_name = "Datacenter Jakarta" if dc_id == 2 else "Datacenter Surabaya"
        vms.append(VirtualMachine(
            id=i + 1,
            name=f"{'JKT' if dc_id == 2 else 'SBY'}_VM{i+1}_{t['name']}",
            mips=round(t["mips"] * multiplier, 1),
            bandwidth_mbps=t["bw"],
            cost_per_mi=t["cost"],
            ram_mb=8192,
            cores=4,
            datacenter_id=dc_id,
            datacenter_name=dc_name
        ))
    return vms


# ============================================================================
# 4. Maheswaran et al. (JPDC 1999) 16-Quadrant ETC Matrix Generator
# ============================================================================

def generate_maheswaran_etc(
    num_tasks: int = 512,
    num_vms: int = 16,
    task_het: str = "high",
    machine_het: str = "high",
    consistency: str = "inconsistent",
    seed: int = 42
) -> Tuple[List[Task], List[VirtualMachine], List[List[float]]]:
    """
    Reproduces the seminal 16-quadrant ETC (Expected Time to Compute) benchmark
    from Maheswaran, Ali, Siegel, Hensgen, Freund (JPDC 1999):
      "Dynamic Mapping of a Class of Independent Tasks onto Heterogeneous Computing Systems"

    Parameters:
      - task_het    : 'high' (U(100, 3000)) or 'low' (U(10, 100))
      - machine_het : 'high' (multiplier U(1, 20)) or 'low' (multiplier U(1, 10))
      - consistency : 'consistent', 'inconsistent', or 'semi-consistent'

    Returns:
      (tasks, vms, etc_matrix) where each Task has its etc_row populated.
    """
    rng = random.Random(seed)

    # 1. Base Task Heterogeneity Range
    if task_het.lower() == "high":
        task_min, task_max = 100.0, 3000.0
    else:
        task_min, task_max = 10.0, 100.0

    # 2. Machine Heterogeneity Factor Range
    if machine_het.lower() == "high":
        mach_min, mach_max = 1.0, 20.0
    else:
        mach_min, mach_max = 1.0, 10.0

    base_machine_multipliers = [rng.uniform(mach_min, mach_max) for _ in range(num_vms)]
    if consistency.lower() == "consistent":
        base_machine_multipliers.sort()  # Machine 0 is consistently fastest, etc.

    etc_matrix: List[List[float]] = []
    tasks: List[Task] = []

    current_arrival = 0.0

    for i in range(num_tasks):
        base_t = rng.uniform(task_min, task_max)
        current_arrival += rng.expovariate(1.0 / 2.0)

        row: List[float] = []
        for j in range(num_vms):
            if consistency.lower() == "consistent":
                exec_time = base_t * base_machine_multipliers[j]
            elif consistency.lower() == "inconsistent":
                # Each machine has an independent random execution factor for this task
                factor = rng.uniform(mach_min, mach_max)
                exec_time = base_t * factor
            elif consistency.lower() == "semi-consistent":
                # Even columns are consistent, odd columns are inconsistent
                if j % 2 == 0:
                    exec_time = base_t * base_machine_multipliers[j]
                else:
                    factor = rng.uniform(mach_min, mach_max)
                    exec_time = base_t * factor
            else:
                exec_time = base_t * rng.uniform(mach_min, mach_max)

            row.append(round(exec_time, 3))

        etc_matrix.append(row)

        tasks.append(Task(
            id=i + 1,
            name=f"Task_{task_het[0].upper()}{machine_het[0].upper()}_{i+1}",
            length_mi=round(base_t, 1),
            file_size_mb=50.0,
            arrival_time=round(current_arrival, 3),
            etc_row=row
        ))

    # Generate VMs with cost rates inversely related to their average execution time
    avg_times = [sum(etc_matrix[i][j] for i in range(num_tasks)) / num_tasks for j in range(num_vms)]
    min_avg = min(avg_times)

    vms: List[VirtualMachine] = []
    for j in range(num_vms):
        # Faster machines (lower avg time) have higher cost rate
        speed_factor = min_avg / avg_times[j]
        cost_rate = round(0.05 + 0.35 * speed_factor, 3)
        vms.append(VirtualMachine(
            id=j + 1,
            name=f"Mach_{j+1}",
            mips=round(100.0 / (avg_times[j] / min_avg), 1),
            bandwidth_mbps=1000.0,
            cost_per_mi=cost_rate
        ))

    return tasks, vms, etc_matrix
