from candidate_transformer.models import SourceRecord, FieldValue
from candidate_transformer.engine.matching import cluster_records, pair_score

def test_pair_score_logic():
    # Helper to build a record fast
    def make_rec(id, fields_dict):
        fvs = []
        for k, v in fields_dict.items():
            fvs.append(FieldValue(field=k, value=v, source="test", method="test"))
        return SourceRecord(source_id=id, source_type="test", fields=fvs)

    # Email match (Strong)
    r1 = make_rec("1", {"full_name": "Jane", "emails": "jane@x.com"})
    r2 = make_rec("2", {"full_name": "Jane D", "emails": "jane@x.com"})
    score, _ = pair_score(r1, r2)
    assert score >= 0.80

    # Name-only match (Must fail)
    r3 = make_rec("3", {"full_name": "John Smith", "phones": "+14155551111"})
    r4 = make_rec("4", {"full_name": "John Smith", "phones": "+12125559999"})
    score, _ = pair_score(r3, r4)
    assert score < 0.80

    # Phone match + Exact name match but no company (0.70 + 0.10 = 0.80 >= threshold -> merges)
    r5 = make_rec("5", {"full_name": "Jane Doe", "phones": "+14155550123"})
    r6 = make_rec("6", {"full_name": "Jane Doe", "phones": "+14155550123", "emails": "diff@x.com"})
    score, _ = pair_score(r5, r6)
    assert score == 0.80

def test_cluster_records():
    fv1 = FieldValue(field="emails", value="jane@x.com", source="csv", method="csv")
    fv2 = FieldValue(field="full_name", value="Jane Doe", source="csv", method="csv")
    r_csv = SourceRecord(source_id="csv_jane", source_type="csv", fields=[fv1, fv2])

    fv3 = FieldValue(field="emails", value="jane@x.com", source="pdf", method="pdf")
    r_pdf = SourceRecord(source_id="pdf_jane", source_type="pdf", fields=[fv3])

    fv4 = FieldValue(field="emails", value="john@x.com", source="csv", method="csv")
    r_john = SourceRecord(source_id="csv_john", source_type="csv", fields=[fv4])

    # Shuffle input to ensure determinism
    clusters = cluster_records([r_pdf, r_john, r_csv])
    
    assert len(clusters) == 2
    # Jane should be merged
    jane_cluster = next(c for c in clusters if len(c.records) == 2)
    assert "csv_jane" in [r.source_id for r in jane_cluster.records]
    assert "pdf_jane" in [r.source_id for r in jane_cluster.records]
    assert "email_match" in jane_cluster.explanation