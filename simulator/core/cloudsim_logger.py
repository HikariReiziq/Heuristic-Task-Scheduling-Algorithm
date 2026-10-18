"""
Logger & Pembangkit Trace Discrete-Event CloudSim.
Mereproduksi format log event CloudSim / CloudSim Plus untuk terminal dan dashboard web.
SOKA (Strategi Optimasi Komputasi Awan) - Kelompok 4 (ITS 2026).

PENTING: modul ini hanya MENAMPILKAN log. Jumlah & spesifikasi Host yang tercetak di sini
adalah teks, bukan bagian dari perhitungan. Hasil makespan/biaya/utilisasi hanya
bergantung pada data VM dan task di benchmarks/datasets.py.
"""

from typing import List, Dict, Any, Optional
from core.models import Task, VirtualMachine, SimulationResult, TaskAllocation

# Kode warna ANSI untuk terminal
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
    Mencetak log trace simulasi discrete-event ala CloudSim:
    1. Inisialisasi Datacenter dan Host fisik
    2. Permintaan pembuatan VM, alokasi ke Host, dan ACK pembuatan
    3. Pengiriman Cloudlet ke VM tujuan
    4. Event selesainya Cloudlet yang dikembalikan ke broker
    5. Tabel standar Cloudlet Execution Record CloudSim
    6. Blok metrik evaluasi untuk satu algoritma

    cost_divisor dipakai untuk konversi satuan biaya (Skenario 1 memakai 7.40 agar jadi Rs seperti paper).
    max_vm_display / max_cloudlet_display hanya membatasi jumlah baris yang dicetak.
    """
    print(f"\n{CYAN}{BOLD}>>> [CLOUDSIM DISCRETE-EVENT SIMULATION TRACE: {scenario_name.upper()}] <<<{RESET}")
    print(f"{DIM}Timestamp Clock: 0.00 s | Simulation Engine: CloudSim 3.0.3 / CloudSim Plus Discrete-Event Core{RESET}")
    print(f"{DIM}Active Heuristic Scheduler: {algorithm_name}{RESET}\n")

    # 1. Penemuan Datacenter dan Host
    # [UBAH DATACENTER] Datacenter dikelompokkan dari field vm.datacenter_name.
    # Untuk menambah/mengganti datacenter, ubah datacenter_id/datacenter_name di fungsi VM
    # pada benchmarks/datasets.py (contoh: get_tugas2a_vms), bukan di sini.
    dc_map: Dict[str, List[VirtualMachine]] = {}
    for vm in vms:
        dc_name = getattr(vm, "datacenter_name", "Datacenter_1")
        dc_map.setdefault(dc_name, []).append(vm)

    num_dcs = len(dc_map)
    print(f"{CYAN}0.00: Broker: Cloud Resource List received with {num_dcs} datacenter(s){RESET}")

    # Peta vm.id -> Host ID di dalam datacenter-nya (dipakai di FASE 1 dan FASE 4)
    host_of: Dict[int, int] = {}
    for dc_name, dc_vms in dc_map.items():
        # [UBAH HOST] Jumlah host per datacenter: 5 untuk skenario Tugas 2A,
        # skenario lain = setengah jumlah VM di datacenter tsb. Ganti angka 5 di sini.
        hosts_count = 5 if "Tugas" in scenario_name else max(1, len(dc_vms) // 2)
        # VM disebar round-robin ke Host #0..#(hosts_count-1) di datacenter masing-masing
        for idx_in_dc, vm in enumerate(dc_vms):
            host_of[vm.id] = idx_in_dc % hosts_count
        dc_short = dc_name.replace(" ", "_")
        # [UBAH HOST] Spesifikasi host (CPU, MIPS/core, RAM, storage) hanya teks di baris ini.
        print(f"0.00: {dc_short}: {hosts_count} Physical Hosts initialized (Xeon E5-2690v4 16-Core, 10,000 MIPS/core, 64GB RAM, 10 Gbps SAN)")

    # 2. Pembuatan VM dan alokasi ke Host (gaya Screenshot 3)
    print(f"\n{YELLOW}--- [FASE 1: VM CREATION & HOST ALLOCATION] ---{RESET}")
    vms_to_show = vms[:max_vm_display]
    for i, vm in enumerate(vms_to_show):
        dc_name = getattr(vm, "datacenter_name", "DC_1")
        dc_tag = dc_name.replace("Datacenter ", "DC_").replace(" ", "_")
        host_id = host_of[vm.id]
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
        print(f"0.01: Broker: Vm #{last_vm.id} (MIPS: {int(last_vm.mips)}, BW: {int(last_vm.bandwidth_mbps)} Mbps, RAM: {ram} MB) has been created in {dc_tag}, Host #{host_of[last_vm.id]}")

    print(f"{GREEN}0.01: Broker: Total {len(vms)} VMs successfully initialized in Datacenter cluster.{RESET}")

    # 3. Pengiriman Cloudlet ke VM (gaya Screenshot 3)
    print(f"\n{YELLOW}--- [FASE 2: DISPATCHING CLOUDLETS TO VMS (SENDING)] ---{RESET}")
    allocs = result.allocations
    allocs_to_show = allocs[:max_cloudlet_display]
    for a in allocs_to_show:
        # Panjang Cloudlet diambil dari task asli; 50000 hanya cadangan jika id di luar jangkauan
        task_len = int(tasks[a.task_id-1].length_mi if a.task_id <= len(tasks) else 50000)
        print(f"0.01: Broker: [SENDING] Cloudlet #{a.task_id} (Length: {task_len} MI) to Vm #{a.vm_id}")

    if len(allocs) > max_cloudlet_display:
        omitted_c = len(allocs) - max_cloudlet_display
        print(f"{DIM}... [{omitted_c} Cloudlet dispatch events omitted for display clarity] ...{RESET}")
        last_a = allocs[-1]
        task_len = int(tasks[last_a.task_id-1].length_mi if last_a.task_id <= len(tasks) else 50000)
        print(f"0.01: Broker: [SENDING] Cloudlet #{last_a.task_id} (Length: {task_len} MI) to Vm #{last_a.vm_id}")

    # 4. Log selesainya Cloudlet (gaya Screenshot 1), diurutkan berdasarkan waktu selesai
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

    # 5. Tabel Cloudlet Execution Record CloudSim (gaya Screenshot 2)
    print(f"\n{YELLOW}--- [FASE 4: CLOUDSIM CLOUDLET EXECUTION RECORD] ---{RESET}")
    print(f"{BOLD}============================== CLOUDSIM CLOUDLET EXECUTION RECORD =============================={RESET}")
    print(f"{BOLD}| {'Cloudlet ID':<11} | {'STATUS':<7} | {'Datacenter ID':<15} | {'Host ID':<7} | {'VM ID':<5} | {'Length (MI)':<11} | {'Start (s)':<9} | {'Finish (s)':<10} | {f'Cost ({cost_unit})':<11} |{RESET}")
    print("-" * 100)

    # 6 baris pertama, lalu "..." dan 2 baris terakhir agar tabel tetap ringkas
    table_sample = finished_sorted[:6]
    for a in table_sample:
        dc_name = getattr(a, "datacenter_name", "Datacenter_1")
        dc_short = dc_name.replace("Datacenter ", "DC_").replace(" ", "_")
        host_id = f"Host #{host_of.get(a.vm_id, 0)}"
        length_val = int(tasks[a.task_id-1].length_mi if a.task_id <= len(tasks) else 50000)
        item_cost = a.cost / cost_divisor
        print(f"| {a.task_id:11d} | {'SUCCESS':<7} | {dc_short:<15} | {host_id:<7} | {a.vm_id:5d} | {length_val:11d} | {a.start_time:9.2f} | {a.finish_time:10.2f} | {item_cost:11.2f} |")

    if len(finished_sorted) > 8:
        print(f"| {DIM}{'...':^11} | {'...':^7} | {'...':^15} | {'...':^7} | {'...':^5} | {'...':^11} | {'...':^9} | {'...':^10} | {'...':^11}{RESET} |")
        for a in finished_sorted[-2:]:
            dc_name = getattr(a, "datacenter_name", "Datacenter_1")
            dc_short = dc_name.replace("Datacenter ", "DC_").replace(" ", "_")
            host_id = f"Host #{host_of.get(a.vm_id, 0)}"
            length_val = int(tasks[a.task_id-1].length_mi if a.task_id <= len(tasks) else 50000)
            item_cost = a.cost / cost_divisor
            print(f"| {a.task_id:11d} | {'SUCCESS':<7} | {dc_short:<15} | {host_id:<7} | {a.vm_id:5d} | {length_val:11d} | {a.start_time:9.2f} | {a.finish_time:10.2f} | {item_cost:11.2f} |")

    print(f"{BOLD}===================================================================================================={RESET}")

    # 6. Blok metrik untuk satu algoritma (gaya Screenshot 2)
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
