from pydantic import BaseModel
from typing import Optional, List, Generic, TypeVar
from datetime import datetime

class ArtistBase(BaseModel):
    artist_short_name: str
    artist_long_name: str
    dob: Optional[str] = None
    dob_place: Optional[str] = None
    dod: Optional[str] = None
    dod_place: Optional[str] = None

class MuseumBase(BaseModel):
    name: str
    name_unique: str
    contact: Optional[str] = None
    profile: Optional[str] = None
    profile_path: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    country_code: Optional[int] = None
    zipcode: Optional[int] = None
    website: Optional[str] = None

class PaintingBase(BaseModel):
    title: str
    unique_title: str
    type: Optional[str] = None
    genre: Optional[str] = None
    materials: Optional[List[str]] = None
    size: Optional[str] = None
    profile: Optional[str] = None
    profile_path: Optional[str] = None
    year: Optional[int] = None
    period: Optional[str] = None
    style: Optional[List[str]] = None

class ArtistResponse(ArtistBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MuseumResponse(MuseumBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PaintingResponse(PaintingBase):
    id: int
    artist: Optional[ArtistResponse] = None
    museum: Optional[MuseumResponse] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

    class Config:
        from_attributes = True