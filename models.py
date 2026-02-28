from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Address:
    id: Optional[int]
    street: str
    notes: str = ""
    active_count: int = 0  # populated by DB query, not stored


@dataclass
class Resident:
    id: Optional[int]
    address_id: int
    first_name: str
    last_name: str
    birth_date: Optional[str] = None       # YYYY-MM-DD
    baptism_date: Optional[str] = None     # YYYY-MM-DD
    marriage_date: Optional[str] = None    # YYYY-MM-DD
    death_date: Optional[str] = None       # YYYY-MM-DD
    status: str = "active"                 # 'active' or 'deceased'
    father: Optional[str] = None
    mother: Optional[str] = None
    spouse: Optional[str] = None
    notes: str = ""

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_baptized(self):
        return self.baptism_date is not None

    @property
    def is_married(self):
        return self.marriage_date is not None or bool(self.spouse)


@dataclass
class Event:
    id: Optional[int]
    resident_id: int
    event_type: str    # 'birth', 'marriage', 'baptism', 'death'
    event_date: str    # YYYY-MM-DD
    description: str = ""
    created_at: str = ""
    resident_name: str = ""  # populated by join query
