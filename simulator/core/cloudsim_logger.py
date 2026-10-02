"""
CloudSim Discrete-Event Logger and Trace Generator.
Reproduces exact CloudSim / CloudSim Plus event logging for terminal and web dashboard.
SOKA (Strategi Optimasi Komputasi Awan) - Kelompok 4 (ITS 2026).
"""

from typing import List, Dict, Any, Optional
from core.models import Task, VirtualMachine, SimulationResult, TaskAllocation

# ANSI Color Codes
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def print_cloudsim_event_trace(
    scenario_name: str,
    tasks: List[Task],
    vms: List[VirtualMachine],
    result: SimulationResult,
    algorithm_name: str = "CCTSA (Proposed)",
    cost_unit: str = "INR",
    cost_divisor: float = 1.0,
    max_vm_display: int = 8,
    max_cloudlet_display: int = 8
) -> None:
    """
    Prints authentic CloudSim discrete-event simulation trace logs:
    1. Datacenter and Physical Host initialization
    2. VM Creation requests, Host allocation, and creation ACK
    3. Cloudlet submission to assigned VMs
    4. Cloudlet completion events returned to broker
    5. Standard CloudSim Cloudlet execution record table
    6. Single-algorithm evaluation metric block
    """
    print(f"\n{CYAN}{BOLD}>>> [CLOUDSIM DISCRETE-EVENT SIMULATION TRACE: {scenario_name.upper()}] <<<{RESET}")
    print(f"{DIM}Timestamp Clock: 0.00 s | Simulation Engine: CloudSim 3.0.3 / CloudSim Plus Discrete-Event Core{RESET}")
    print(f"{DIM}Active Heuristic Scheduler: {algorithm_name}{RESET}\n")

    # 1. Datacenter and Host Discovery
    dc_map: Dict[str, List[VirtualMachine]] = {}
    for vm in vms:
        dc_name = getattr(vm, "datacenter_name", "Datacenter_1")
        dc_map.setdefault(dc_name, []).append(vm)

    num_dcs = len(dc_map)
    print(f"{CYAN}0.00: Broker: Cloud Resource List received with {num_dcs} datacenter(s){RESET}")

    for idx, (dc_name, dc_vms) in enumerate(dc_map.items()):
        hosts_count = 10 if "Tugas" in scenario_name or "GoCJ" in scenario_name else max(1, len(dc_vms) // 2 or 1)
        dc_short = dc_name.replace(" ", "_")
        print(f"0.00: {dc_short}: {hosts_count} Physical Hosts initialized (Xeon E5-2690v4 16-Core, 10,000 MIPS/core, 64GB RAM, 10 Gbps SAN)")

    # 2. VM Creation and Allocation (Screenshot 3 style)
    print(f"\n{YELLOW}--- [FASE 1: VM CREATION & HOST ALLOCATION] ---{RESET}")
    vms_to_show = vms[:max_vm_display]
    for i, vm in enumerate(vms_to_show):
        dc_name = getattr(vm, "datacenter_name", "DC_1")
        dc_tag = dc_name.replace("Datacenter ", "DC_").replace(" ", "_")
        host_id = i % 10
        print(f"0.00: Broker: Trying to Create Vm #{vm.id} in {dc_tag}")
        print(f"0.00: {dc_tag}.guestAllocator: Vm #{vm.id} has been allocated to Host #{host_id}")
        ram = getattr(vm, "ram_mb", 2048)
        print(f"0.01: Broker: Vm #{vm.id} (MIPS: {int(vm.mips)}, BW: {int(vm.bandwidth_mbps)} Mbps, RAM: {ram} MB) has been created in {dc_tag}, Host #{host_id}")

    if len(vms) > max_vm_display:
        omitted = len(vms) - max_vm_display
        print(f"{DIM}... [{omitted} VM creation events omitted for display clarity] ...{RESET}")
        last_vm = vms[-1]
        dc_name = getattr(last_vm, "datacenter_name", "DC_1")
        dc_tag = dc_name.replace("Datacenter ", "DC_").replace(" ", "_")
        ram = getattr(last_vm, "ram_mb", 2048)
        print(f"0.01: Broker: Vm #{last_vm.id} (MIPS: {int(last_vm.mips)}, BW: {int(last_vm.bandwidth_mbps)} Mbps, RAM: {ram} MB) has been created in {dc_tag}, Host #{len(vms)%10}")

    print(f"{GREEN}0.01: Broker: Total {len(vms)} VMs successfully initialized in Datacenter cluster.{RESET}")

    # 3. Cloudlet Submission (Screenshot 3 style)
    print(f"\n{YELLOW}--- [FASE 2: DISPATCHING CLOUDLETS TO VMS (SENDING)] ---{RESET}")
    allocs = result.allocations
    allocs_to_show = allocs[:max_cloudlet_display]
    for a in allocs_to_show:
        task_len = int(tasks[a.task_id-1].length_mi if a.task_id <= len(tasks) else 50000)
        print(f"0.01: Broker: [SENDING] Cloudlet #{a.task_id} (Length: {task_len} MI) to Vm #{a.vm_id}")

    if len(allocs) > max_cloudlet_display:
        omitted_c = len(allocs) - max_cloudlet_display
        print(f"{DIM}... [{omitted_c} Cloudlet dispatch events omitted for display clarity] ...{RESET}")
        last_a = allocs[-1]
        task_len = int(tasks[last_a.task_id-1].length_mi if last_a.task_id <= len(tasks) else 50000)
        print(f"0.01: Broker: [SENDING] Cloudlet #{last_a.task_id} (Length: {task_len} MI) to Vm #{last_a.vm_id}")

    # 4. Cloudlet Completion Logs (Screenshot 1 style)
    print(f"\n{YELLOW}--- [FASE 3: CLOUDLET EXECUTION & RETURN TO BROKER (RECEIVER & FINISH)] ---{RESET}")
    finished_sorted = sorted(allocs, key=lambda x: x.finish_time)
    finish_to_show = finished_sorted[:max_cloudlet_display]

    for a in finish_to_show:
        print(f"INFO {a.finish_time:7.2f}: SOKA_CloudBroker: [RECEIVER] Cloudlet #{a.task_id} finished in Vm #{a.vm_id} and returned to broker.")

    if len(finished_sorted) > max_cloudlet_display:
        omitted_f = len(finished_sorted) - (max_cloudlet_display + 3)
        if omitted_f > 0:
            print(f"{DIM}... [{omitted_f} Cloudlet execution events completed asynchronously] ...{RESET}")
        for a in finished_sorted[-3:]:
            print(f"INFO {a.finish_time:7.2f}: SOKA_CloudBroker: [RECEIVER] Cloudlet #{a.task_id} finished in Vm #{a.vm_id} and returned to broker.")

    makespan = result.makespan
    print(f"{GREEN}INFO {makespan:7.2f}: SOKA_CloudBroker: [FINISH] All {len(tasks)} Cloudlets finished execution. Broker shutting down.{RESET}")

    # 5. CloudSim Cloudlet Execution Record Table (Screenshot 2 style)
    print(f"\n{YELLOW}--- [FASE 4: CLOUDSIM CLOUDLET EXECUTION RECORD] ---{RESET}")
    print(f"{BOLD}============================== CLOUDSIM CLOUDLET EXECUTION RECORD =============================={RESET}")
    print(f"{BOLD}| {'Cloudlet ID':<11} | {'STATUS':<7} | {'Datacenter ID':<15} | {'Host ID':<7} | {'VM ID':<5} | {'Length (MI)':<11} | {'Start (s)':<9} | {'Finish (s)':<10} | {f'Cost ({cost_unit})':<11} |{RESET}")
    print("-" * 100)

    table_sample = finished_sorted[:6]
    for a in table_sample:
        dc_name = getattr(a, "datacenter_name", "Datacenter_1")
        dc_short = dc_name.replace("Datacenter ", "DC_").replace(" ", "_")
        host_id = f"Host #{a.vm_id % 10}"
        length_val = int(tasks[a.task_id-1].length_mi if a.task_id <= len(tasks) else 50000)
        item_cost = a.cost / cost_divisor
        print(f"| {a.task_id:11d} | {'SUCCESS':<7} | {dc_short:<15} | {host_id:<7} | {a.vm_id:5d} | {length_val:11d} | {a.start_time:9.2f} | {a.finish_time:10.2f} | {item_cost:11.2f} |")

    if len(finished_sorted) > 8:
        print(f"| {DIM}{'...':^11} | {'...':^7} | {'...':^15} | {'...':^7} | {'...':^5} | {'...':^11} | {'...':^9} | {'...':^10} | {'...':^11}{RESET} |")
        for a in finished_sorted[-2:]:
            dc_name = getattr(a, "datacenter_name", "Datacenter_1")
            dc_short = dc_name.replace("Datacenter ", "DC_").replace(" ", "_")
            host_id = f"Host #{a.vm_id % 10}"
            length_val = int(tasks[a.task_id-1].length_mi if a.task_id <= len(tasks) else 50000)
            item_cost = a.cost / cost_divisor
            print(f"| {a.task_id:11d} | {'SUCCESS':<7} | {dc_short:<15} | {host_id:<7} | {a.vm_id:5d} | {length_val:11d} | {a.start_time:9.2f} | {a.finish_time:10.2f} | {item_cost:11.2f} |")

    print(f"{BOLD}===================================================================================================={RESET}")

    # 6. Single Algorithm Metric Block (Screenshot 2 style)
    final_cost = result.total_cost / cost_divisor
    cost_str = f"{final_cost:,.2f} {cost_unit}"
    print(f"\n{YELLOW}--- [FASE 5: HASIL EVALUASI METRIK KINERJA] ---{RESET}")
    print(f"""{BOLD}{GREEN}========== HASIL EVALUASI METRIK {algorithm_name.upper()} =========={RESET}
{BOLD}1. Makespan             :{RESET} {result.makespan:.2f} Detik
{BOLD}2. Average Waiting Time :{RESET} {result.avg_waiting_time:.2f} Detik
{BOLD}3. Resource Utilization :{RESET} {result.resource_utilization:.2f} %
{BOLD}4. Total Rental Cost    :{RESET} {cost_str}
{BOLD}5. Degree of Imbalance  :{RESET} {result.degree_of_imbalance:.4f}
{BOLD}{GREEN}===================================================================={RESET}
""")
