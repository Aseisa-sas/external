from pydantic import BaseModel
from typing import Optional

class AdresResponse(BaseModel):
    """
    Standardized response model for ADRES queries.
    """
    type_identity: Optional[str] = None
    identity: Optional[str] = None
    names: Optional[str] = None
    last_names: Optional[str] = None
    birthday: Optional[str] = None
    province: Optional[str] = None
    municipality: Optional[str] = None
    status: Optional[str] = None
    entity: Optional[str] = None
    regime: Optional[str] = None
    effective_date_membership: Optional[str] = None
    end_date_membership: Optional[str] = None
    type_member: Optional[str] = None
