from pydantic import BaseModel, Field, field_validator

class Location(BaseModel):
    city: str | None = None
    region: str | None = None
    country: str | None = None

class Links(BaseModel):
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None
    other: list[str] = []

class Skill(BaseModel):
    name: str
    confidence: float
    sources: list[str] = []

class ExperienceItem(BaseModel):
    company: str | None = None
    title: str | None = None
    start: str | None = None
    end: str | None = None
    summary: str | None = None

class EducationItem(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    end_year: int | None = None

class Provenance(BaseModel):
    field: str
    source: str
    method: str

class CanonicalProfile(BaseModel):
    candidate_id: str
    full_name: str | None = None
    emails: list[str] = []
    phones: list[str] = []
    location: Location = Field(default_factory=Location)
    links: Links = Field(default_factory=Links)
    headline: str | None = None
    years_experience: float | None = None
    skills: list[Skill] = []
    experience: list[ExperienceItem] = []
    education: list[EducationItem] = []
    provenance: list[Provenance] = []
    overall_confidence: float = 0.0

    @field_validator('overall_confidence')
    @classmethod
    def check_confidence_bounds(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError('overall_confidence must be between 0.0 and 1.0')
        return v