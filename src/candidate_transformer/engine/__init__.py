from .matching import cluster_records, Cluster
from .conflict import resolve_cluster, resolve_field, ResolvedField
from .confidence import calculate_confidence, compute_overall_confidence

__all__ = [
    "cluster_records", "Cluster", 
    "resolve_cluster", "resolve_field", "ResolvedField",
    "calculate_confidence", "compute_overall_confidence"
]