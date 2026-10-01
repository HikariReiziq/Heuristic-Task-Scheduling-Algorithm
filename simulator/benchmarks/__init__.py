"""Benchmarks package."""
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

__all__ = [
    "get_paper_table1_vms",
    "get_paper_table2_tasks",
    "get_paper_reference_results",
    "generate_heterogeneous_vms",
    "generate_synthetic_workload",
    "get_gocj_workload",
    "generate_gocj_vms",
    "get_tugas2a_workload",
    "get_tugas2a_vms",
    "generate_maheswaran_etc"
]
