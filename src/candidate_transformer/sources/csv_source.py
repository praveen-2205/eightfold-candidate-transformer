import csv
import os
from candidate_transformer.models import SourceRecord, FieldValue
from candidate_transformer.normalize import to_e164, normalize_email
from candidate_transformer.util.logging import get_logger

logger = get_logger(__name__)

class CsvSource:
    source_type = "recruiter_csv"
    
    def load(self, path: str) -> list[SourceRecord]:
        if not os.path.exists(path):
            logger.warning(f"File not found: {path}")
            return []
            
        records = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    try:
                        fields = []
                        
                        # 1. Full Name
                        if row.get("name"):
                            fields.append(FieldValue(
                                field="full_name", value=row["name"].strip(),
                                source=self.source_type, method="csv_field",
                                raw=row["name"], extraction_confidence=0.9
                            ))
                            
                        # 2. Emails
                        if row.get("email"):
                            raw_emails = [e.strip() for e in row["email"].replace(";", ",").split(",") if e.strip()]
                            for email in raw_emails:
                                norm_email = normalize_email(email)
                                if norm_email:
                                    fields.append(FieldValue(
                                        field="emails", value=norm_email,
                                        source=self.source_type, method="csv_field+normalized:email",
                                        raw=email, extraction_confidence=0.9
                                    ))
                                    
                        # 3. Phones
                        if row.get("phone"):
                            raw_phone = row["phone"].strip()
                            norm_phone = to_e164(raw_phone)
                            if norm_phone:
                                fields.append(FieldValue(
                                    field="phones", value=norm_phone,
                                    source=self.source_type, method="csv_field+normalized:E164",
                                    raw=raw_phone, extraction_confidence=0.9
                                ))
                                
                        # 4. Experience (Company & Title formatted directly for canonical merging)
                        if row.get("latest_company") or row.get("title"):
                            company = row.get("latest_company", "").strip() or None
                            title = row.get("title", "").strip() or None
                            fields.append(FieldValue(
                                field="experience", 
                                value={"company": company, "title": title, "start": None, "end": None, "summary": None},
                                source=self.source_type, method="csv_field",
                                raw={"latest_company": company, "title": title}, extraction_confidence=0.9
                            ))
                            
                        records.append(SourceRecord(
                            source_id=f"{os.path.basename(path)}_row_{i}",
                            source_type=self.source_type,
                            fields=fields
                        ))
                    except Exception as e:
                        logger.warning(f"Skipping malformed row {i} in {path}: {e}")
                        
        except Exception as e:
            logger.warning(f"Failed to read CSV {path}: {e}")
            
        return records