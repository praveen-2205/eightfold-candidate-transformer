from candidate_transformer.models import FieldValue, SourceRecord
from candidate_transformer.engine.matching import Cluster
from candidate_transformer.engine.conflict import resolve_field, resolve_cluster

def test_resolve_single_value_conflict():
    fv_csv = FieldValue(field="current_title", value="Senior Engineer", source="recruiter_csv", method="csv_field")
    fv_llm = FieldValue(field="current_title", value="ML Engineer", source="resume:1.pdf", method="resume_llm")
    
    # CSV should beat resume_llm based on source & method reliability
    resolved = resolve_field("current_title", [fv_llm, fv_csv])
    assert len(resolved.winners) == 1
    assert resolved.winners[0].value == "Senior Engineer"
    assert len(resolved.losers) == 1
    assert resolved.losers[0].value == "ML Engineer"

def test_resolve_array_union():
    fv1 = FieldValue(field="emails", value="jane@x.com", source="recruiter_csv", method="csv_field")
    fv2 = FieldValue(field="emails", value="jane@x.com", source="resume:1.pdf", method="resume_regex")
    fv3 = FieldValue(field="emails", value="other@x.com", source="github", method="regex")
    
    resolved = resolve_field("emails", [fv1, fv2, fv3])
    # Should dedupe jane@x.com and keep other@x.com
    assert len(resolved.winners) == 2
    assert {"jane@x.com", "other@x.com"} == {w.value for w in resolved.winners}
    assert len(resolved.losers) == 1
    assert resolved.losers[0].value == "jane@x.com"

def test_resolve_cluster_integration():
    r1 = SourceRecord(
        source_id="1", source_type="recruiter_csv",
        fields=[
            FieldValue(field="full_name", value="Jane Doe", source="recruiter_csv", method="csv"),
            FieldValue(field="emails", value="j@x.com", source="recruiter_csv", method="csv")
        ]
    )
    r2 = SourceRecord(
        source_id="2", source_type="resume",
        fields=[
            FieldValue(field="full_name", value="Jane D.", source="resume", method="regex"),
            FieldValue(field="emails", value="j@x.com", source="resume", method="regex")
        ]
    )
    
    cluster = Cluster(id="c1", records=[r1, r2])
    resolved_map = resolve_cluster(cluster)
    
    assert resolved_map["full_name"].winners[0].value == "Jane Doe"
    assert len(resolved_map["emails"].winners) == 1
    assert resolved_map["emails"].winners[0].value == "j@x.com"