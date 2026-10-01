"""
Cloud Simulation Engine & Broker.
Inspired by CloudSim Plus / ansul2k/cloud-simulator architecture.
Orchestrates task submissions, VM pools, and scheduling execution.
Designed for SOKA - Kelompok 4 (ITS 2026).
"""

from typing import List, Dict, Any, Type
import copy
from core.models import Task, VirtualMachine, SimulationResult
from schedulers.base import BaseScheduler

class CloudBroker:
    """
    Acts as the Datacenter Broker / Global Scheduler in CloudSim.
    Receives tasks from Cloud Consumers and maps them to Virtual Machines
    according to the active scheduling heuristic.
    """

    def __init__(self, name: str = "SOKA_CloudBroker"):
        self.name = name
        self.registered_schedulers: Dict[str, BaseScheduler] = {}

    def register_scheduler(self, scheduler: BaseScheduler) -> None:
        """Register a scheduling algorithm with the broker."""
        self.registered_schedulers[scheduler.name] = scheduler

    def run_single(
        self,
        scheduler_name: str,
        tasks: List[Task],
        vms: List[VirtualMachine]
    ) -> SimulationResult:
        """Run a single scheduler on deep copies of tasks and VMs."""
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
        Executes all registered schedulers under identical initial conditions.
        Returns a dictionary mapping scheduler name to its SimulationResult.
        """
        results: Dict[str, SimulationResult] = {}
        for name, scheduler in self.registered_schedulers.items():
            tasks_copy = [copy.deepcopy(t) for t in tasks]
            vms_copy = [copy.deepcopy(v) for v in vms]
            results[name] = scheduler.schedule(tasks_copy, vms_copy)
        return results
