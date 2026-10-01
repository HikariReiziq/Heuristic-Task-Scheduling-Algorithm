"""
Automated Unit Tests & Verification Suite for Cloud Task Scheduling Simulator.
Tests core models, metrics, schedulers, and dataset integrity.
Run with: python3 -m unittest test_simulator.py
"""

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from core.models import Task, VirtualMachine, TaskAllocation
from core.metrics import (
    calculate_makespan,
    calculate_total_cost,
    calculate_resource_utilization,
    calculate_degree_of_imbalance,
    calculate_avg_waiting_time
)
from benchmarks.datasets import (
    get_paper_table1_vms,
    get_paper_table2_tasks,
    get_paper_reference_results,
    generate_heterogeneous_vms,
    generate_synthetic_workload,
    get_gocj_workload,
    generate_gocj_vms,
    get_tugas2a_workload,
    get_tugas2a_vms,
    generate_maheswaran_etc
)
from schedulers import (
    CCTSAScheduler,
    ETSAScheduler,
    StandardSufferageScheduler,
    MinMinScheduler,
    RoundRobinScheduler
)
from engine import CloudBroker


class TestCloudSimulator(unittest.TestCase):

    def setUp(self):
        self.vms = get_paper_table1_vms()
        self.tasks = get_paper_table2_tasks()

    def test_table1_vms_specification(self):
        """Verify Table I specifications match paper exactly."""
        self.assertEqual(len(self.vms), 3)
        self.assertEqual(self.vms[0].mips, 50.0)
        self.assertEqual(self.vms[0].bandwidth_mbps, 100.0)
        self.assertEqual(self.vms[0].cost_per_mi, 0.03)

        self.assertEqual(self.vms[1].mips, 100.0)
        self.assertEqual(self.vms[1].bandwidth_mbps, 200.0)
        self.assertEqual(self.vms[1].cost_per_mi, 0.12)

        self.assertEqual(self.vms[2].mips, 200.0)
        self.assertEqual(self.vms[2].bandwidth_mbps, 250.0)
        self.assertEqual(self.vms[2].cost_per_mi, 0.24)

    def test_table2_tasks_specification(self):
        """Verify Table II specifications match paper exactly."""
        self.assertEqual(len(self.tasks), 10)
        self.assertEqual(self.tasks[0].length_mi, 206.0)
        self.assertEqual(self.tasks[0].file_size_mb, 44.0)

        self.assertEqual(self.tasks[9].length_mi, 45.0)
        self.assertEqual(self.tasks[9].file_size_mb, 23.0)

        total_mi = sum(t.length_mi for t in self.tasks)
        self.assertEqual(total_mi, 1039.0)

    def test_etc_matrix_computation(self):
        """Verify Equation (2): ET = MI/MIPS + Mb/Mbps."""
        etc = CCTSAScheduler.compute_etc_matrix(self.tasks, self.vms)
        self.assertEqual(len(etc), 10)
        self.assertEqual(len(etc[0]), 3)

        # Task 1 on R1: 206/50 + 44/100 = 4.12 + 0.44 = 4.56 s
        self.assertAlmostEqual(etc[0][0], 4.56, places=4)
        # Task 1 on R2: 206/100 + 44/200 = 2.06 + 0.22 = 2.28 s
        self.assertAlmostEqual(etc[0][1], 2.28, places=4)
        # Task 1 on R3: 206/200 + 44/250 = 1.03 + 0.176 = 1.206 s
        self.assertAlmostEqual(etc[0][2], 1.206, places=4)

    def test_ecc_matrix_computation(self):
        """Verify Equation (3): Cost = MI * CostRate."""
        ecc = CCTSAScheduler.compute_ecc_matrix(self.tasks, self.vms)
        self.assertEqual(len(ecc), 10)
        self.assertEqual(len(ecc[0]), 3)

        # Task 1 on R1: 206 * 0.03 = 6.18
        self.assertAlmostEqual(ecc[0][0], 6.18, places=4)
        # Task 1 on R2: 206 * 0.12 = 24.72
        self.assertAlmostEqual(ecc[0][1], 24.72, places=4)
        # Task 1 on R3: 206 * 0.24 = 49.44
        self.assertAlmostEqual(ecc[0][2], 49.44, places=4)

    def test_metrics_calculation(self):
        """Test calculation functions for makespan, cost, RU, DI."""
        times = {1: 3.62, 2: 3.345, 3: 4.172}
        ms = calculate_makespan(times)
        self.assertAlmostEqual(ms, 4.172, places=3)

        ru = calculate_resource_utilization(times, ms)
        # sum = 11.137 / (3 * 4.172) = 11.137 / 12.516 = 88.98%
        self.assertAlmostEqual(ru, 88.98, places=1)

        di = calculate_degree_of_imbalance(times)
        self.assertTrue(di >= 0.0)

    def test_cctsa_execution(self):
        """Ensure CCTSA executes cleanly and produces valid allocations for all tasks."""
        scheduler = CCTSAScheduler()
        result = scheduler.schedule(self.tasks, self.vms)
        self.assertEqual(result.num_tasks, 10)
        self.assertEqual(result.num_vms, 3)
        self.assertEqual(len(result.allocations), 10)
        self.assertTrue(result.makespan > 0.0)
        self.assertTrue(result.total_cost > 0.0)
        self.assertTrue(result.resource_utilization > 0.0)

    def test_all_schedulers_comparative_broker(self):
        """Ensure broker executes all registered schedulers without errors."""
        broker = CloudBroker()
        broker.register_scheduler(CCTSAScheduler())
        broker.register_scheduler(ETSAScheduler())
        broker.register_scheduler(StandardSufferageScheduler())
        broker.register_scheduler(MinMinScheduler())
        broker.register_scheduler(RoundRobinScheduler())

        results = broker.run_comparative_benchmark(self.tasks, self.vms)
        self.assertEqual(len(results), 5)
        for name, res in results.items():
            self.assertEqual(res.num_tasks, 10)
            self.assertEqual(len(res.allocations), 10)
            self.assertTrue(res.makespan > 0.0)

    def test_synthetic_workload_generator(self):
        """Test Poisson/normal synthetic workload generator."""
        tasks_50 = generate_synthetic_workload(50, seed=123)
        self.assertEqual(len(tasks_50), 50)
        for t in tasks_50:
            self.assertTrue(t.length_mi >= 20.0)
            self.assertTrue(t.file_size_mb >= 20.0)
            self.assertTrue(t.arrival_time >= 0.0)

    def test_gocj_workload_generator(self):
        """Test GoCJ real-world workload generator (Small, Medium, Large, Extra-Large)."""
        tasks = get_gocj_workload(num_tasks=100, seed=42)
        self.assertEqual(len(tasks), 100)
        for t in tasks:
            self.assertTrue(10_000.0 <= t.length_mi <= 500_000.0)
            self.assertTrue(100.0 <= t.file_size_mb <= 1000.0)
            self.assertTrue(t.arrival_time >= 0.0)

        vms = generate_gocj_vms(num_vms=10)
        self.assertEqual(len(vms), 10)
        for v in vms:
            self.assertTrue(v.mips >= 2500.0)
            self.assertTrue(v.cost_per_mi > 0.0)

    def test_tugas2a_workload_and_vms(self):
        """Test SOKA Tugas 2A benchmark specifications (50.000 MI, 400 MB)."""
        tasks = get_tugas2a_workload(num_tasks=50, seed=42)
        self.assertEqual(len(tasks), 50)
        for t in tasks:
            self.assertEqual(t.length_mi, 50_000.0)
            self.assertEqual(t.file_size_mb, 400.0)

        vms = get_tugas2a_vms(num_vms=20)
        self.assertEqual(len(vms), 20)
        for v in vms:
            self.assertEqual(v.cores, 4)
            self.assertEqual(v.ram_mb, 8192)

    def test_maheswaran_etc_generator(self):
        """Test Maheswaran et al. (JPDC 1999) 16-quadrant ETC matrix generator."""
        tasks, vms, etc_matrix = generate_maheswaran_etc(
            num_tasks=64, num_vms=8, task_het="high", machine_het="high", consistency="inconsistent", seed=42
        )
        self.assertEqual(len(tasks), 64)
        self.assertEqual(len(vms), 8)
        self.assertEqual(len(etc_matrix), 64)
        self.assertEqual(len(etc_matrix[0]), 8)

        # Ensure Task.etc_row is populated
        for t in tasks:
            self.assertIsNotNone(t.etc_row)
            self.assertEqual(len(t.etc_row), 8)

        # Run CCTSA on this Maheswaran matrix
        cctsa = CCTSAScheduler()
        res = cctsa.schedule(tasks, vms)
        self.assertEqual(res.num_tasks, 64)
        self.assertEqual(res.num_vms, 8)
        self.assertTrue(res.makespan > 0.0)
        self.assertTrue(res.resource_utilization > 0.0)


if __name__ == "__main__":
    unittest.main()

