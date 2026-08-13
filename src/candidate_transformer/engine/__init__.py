from .matching import cluster_records, Cluster
from .conflict import resolve_cluster, resolve_field, ResolvedField
from .confidence import calculate_confidence, compute_overall_confidence
from .provenance import build_provenance

__all__ = [
    "cluster_records", "Cluster", 
    "resolve_cluster", "resolve_field", "ResolvedField",
    "calculate_confidence", "compute_overall_confidence",
    "build_provenance"
]