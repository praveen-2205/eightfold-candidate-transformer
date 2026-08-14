from collections import defaultdict
from dataclasses import dataclass, field
from rapidfuzz import fuzz

from candidate_transformer.models import SourceRecord
from candidate_transformer.util.logging import get_logger

logger = get_logger(__name__)

MATCH_THRESHOLD = 0.80

@dataclass
class Cluster:
    id: str
    records: list[SourceRecord]
    explanation: list[str] = field(default_factory=list)

def _get_values(record: SourceRecord, field_name: str) -> set[str]:
    return {f.value for f in record.fields if f.field == field_name and f.value}

def _get_name_similarity(rec_a: SourceRecord, rec_b: SourceRecord) -> float:
    names_a = _get_values(rec_a, "full_name")
    names_b = _get_values(rec_b, "full_name")
    if not names_a or not names_b:
        return 0.0
    best = 0.0
    for na in names_a:
        for nb in names_b:
            score = fuzz.WRatio(na.lower(), nb.lower()) / 100.0
            if score > best:
                best = score
    return best

def pair_score(a: SourceRecord, b: SourceRecord) -> tuple[float, list[str]]:
    """Scores a pair of records. Name-only matches can never reach the threshold."""
    score = 0.0
    explanations = []

    # 1. Emails (+1.00)
    emails_a = _get_values(a, "emails")
    emails_b = _get_values(b, "emails")
    if emails_a & emails_b:
        score += 1.00
        explanations.append("email_match")

    # 2. URLs (+0.80)
    for url_field in ["links.github", "links.linkedin"]:
        if _get_values(a, url_field) & _get_values(b, url_field):
            score += 0.80
            explanations.append(f"{url_field.split('.')[-1]}_match")

    # 3. Phones (+0.70)
    if _get_values(a, "phones") & _get_values(b, "phones"):
        score += 0.70
        explanations.append("phone_match")

    # 4. Name + Company Signals
    name_sim = _get_name_similarity(a, b)
    if name_sim >= 0.90:
        def extract_companies(rec: SourceRecord) -> set[str]:
            comps = _get_values(rec, "latest_company")
            for f in rec.fields:
                if f.field == "experience" and isinstance(f.value, dict) and f.value.get("company"):
                    comps.add(f.value["company"])
            return {c.lower() for c in comps if isinstance(c, str)}
            
        comps_a = extract_companies(a)
        comps_b = extract_companies(b)
        
        if comps_a & comps_b:
            score += 0.30
            explanations.append(f"name_and_company_match")
        else:
            score += 0.10
            explanations.append(f"name_only_match")

    return min(round(score, 2), 1.0), explanations

def cluster_records(records: list[SourceRecord]) -> list[Cluster]:
    if not records:
        return []
        
    # Sort deterministically
    sorted_records = sorted(records, key=lambda r: r.source_id)
    
    # Setup Union-Find (Disjoint Set)
    parent = {r.source_id: r.source_id for r in sorted_records}
    
    def find(i: str) -> str:
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]
        
    def union(i: str, j: str):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            # Deterministic merge
            if root_i < root_j:
                parent[root_j] = root_i
            else:
                parent[root_i] = root_j

    explanations_map = defaultdict(list)
    
    # Blocking: bucket records by cheap keys to avoid O(n^2) scaling issues
    buckets = defaultdict(list)
    for r in sorted_records:
        keys: set[str] = set()
        keys.update(f"email:{v}" for v in _get_values(r, "emails"))
        keys.update(f"phone:{v}" for v in _get_values(r, "phones"))
        keys.update(f"gh:{v}" for v in _get_values(r, "links.github"))
        keys.update(f"li:{v}" for v in _get_values(r, "links.linkedin"))
        
        names = list(_get_values(r, "full_name"))
        if names:
            parts = names[0].split()
            if parts:
                keys.add(f"lname_init:{parts[-1][0].lower()}")
                
        if not keys:
            keys.add("unblocked")
            
        for k in keys:
            buckets[k].append(r)
            
    # Pairwise comparison only within buckets
    compared = set()
    for bucket_key, block_records in buckets.items():
        for i in range(len(block_records)):
            for j in range(i + 1, len(block_records)):
                ra, rb = block_records[i], block_records[j]
                pair_id = tuple(sorted([ra.source_id, rb.source_id]))
                if pair_id in compared:
                    continue
                compared.add(pair_id)
                
                score, expl = pair_score(ra, rb)
                if score >= MATCH_THRESHOLD:
                    union(ra.source_id, rb.source_id)
                    explanations_map[pair_id].extend(expl)

    # Group into final Clusters
    clusters_map = defaultdict(list)
    for r in sorted_records:
        clusters_map[find(r.source_id)].append(r)
        
    result = []
    for root_id, cluster_recs in sorted(clusters_map.items()):
        cluster_id = f"cluster_{root_id}"
        
        cluster_expl = set()
        for i in range(len(cluster_recs)):
            for j in range(i + 1, len(cluster_recs)):
                pair_id = tuple(sorted([cluster_recs[i].source_id, cluster_recs[j].source_id]))
                if pair_id in explanations_map:
                    cluster_expl.update(explanations_map[pair_id])
                    
        result.append(Cluster(
            id=cluster_id,
            records=cluster_recs,
            explanation=sorted(list(cluster_expl))
        ))
        
    return result