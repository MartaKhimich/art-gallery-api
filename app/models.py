from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Artist(Base):
    __tablename__ = "artists"
    
    id = Column(Integer, primary_key=True, index=True)
    artist_short_name = Column(String(100), nullable=False)
    artist_long_name = Column(String(200), nullable=False)
    dob = Column(String(10))
    dob_place = Column(String(200))
    dod = Column(String(10))
    dod_place = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    paintings = relationship("Painting", back_populates="artist")

class Museum(Base):
    __tablename__ = "museums"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    name_unique = Column(String(100), unique=True)
    contact = Column(String(100))
    profile = Column(String(255))
    profile_path = Column(String(500))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    country_code = Column(Integer)
    zipcode = Column(Integer)
    website = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    paintings = relationship("Painting", back_populates="museum")

class Painting(Base):
    __tablename__ = "paintings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    unique_title = Column(String(100), unique=True)
    type = Column(String(50))
    genre = Column(String(100))
    materials = Column(JSON)
    size = Column(String(100))
    profile = Column(String(255))
    profile_path = Column(String(500))
    year = Column(Integer)
    period = Column(String(100))
    style = Column(JSON)
    
    artist_id = Column(Integer, ForeignKey("artists.id"))
    museum_id = Column(Integer, ForeignKey("museums.id"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    artist = relationship("Artist", back_populates="paintings")
    museum = relationship("Museum", back_populates="paintings")