from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

class BenutzerCreate(BaseModel):
    vorname: str
    nachname: str
    rolle: str
    email: str

class BenutzerOut(BenutzerCreate):
    id: int
    class Config:
        orm_mode = True

class FahrzeugtypCreate(BaseModel):
    name: str
    anzahl_verfuegbar: int

class FahrzeugtypOut(FahrzeugtypCreate):
    id: int
    class Config:
        orm_mode = True

class TransportCreate(BaseModel):
    von: str
    nach: str
    fahrzeugtyp: str
    datum: date
    startzeit: str
    zeitfenster: datetime
    status: Optional[str] = "offen"
    begruendung: Optional[str] = None
    fahrer_id: Optional[int] = None
    mehrfachtransport_id: Optional[int] = None

class TransportOut(TransportCreate):
    id: int
    distanz_m: Optional[int] = None
    class Config:
        orm_mode = True

class MehrfachtransportRouteCreate(BaseModel):
    von: str
    nach: str
    reihenfolge: int

class MehrfachtransportCreate(BaseModel):
    name: str
    fahrzeugtyp: str
    datum: date
    startzeit: str
    routen: List[MehrfachtransportRouteCreate]
    fahrer_id: Optional[int] = None

class MehrfachtransportOut(BaseModel):
    id: int
    name: str
    fahrzeugtyp: str
    datum: date
    startzeit: str
    status: str
    gesamt_distanz_m: Optional[int] = None
    fahrer_id: Optional[int] = None
    erstellt_am: datetime
    class Config:
        orm_mode = True

class TransportUpdate(BaseModel):
    von: Optional[str] = None
    nach: Optional[str] = None
    fahrzeugtyp: Optional[str] = None
    datum: Optional[date] = None
    startzeit: Optional[str] = None
    weg_min: Optional[float] = None
    zeitfenster: Optional[datetime] = None
    status: Optional[str] = None
    begruendung: Optional[str] = None
    fahrer_id: Optional[int] = None

class ZeitfensterCreate(BaseModel):
    start: datetime
    ende: datetime
    verfuegbar: Optional[str] = "true"

class ZeitfensterOut(ZeitfensterCreate):
    id: int
    class Config:
        orm_mode = True

class SchichtCreate(BaseModel):
    von: datetime
    bis: datetime
    pause_min: Optional[int] = 0
    fahrer_id: int

class SchichtOut(SchichtCreate):
    id: int
    class Config:
        orm_mode = True

class LogbuchCreate(BaseModel):
    aktion: str
    zeitpunkt: datetime
    benutzer_id: int

class LogbuchOut(LogbuchCreate):
    id: int
    class Config:
        orm_mode = True

class DistanzCreate(BaseModel):
    von: str
    nach: str
    distanz_m: float

class DistanzOut(DistanzCreate):
    id: int
    class Config:
        orm_mode = True

class ArchivTransportCreate(BaseModel):
    von: str
    nach: str
    fahrzeugtyp: str
    status: str
    abgeschlossen_am: datetime
    begruendung: Optional[str] = None

class ArchivTransportOut(ArchivTransportCreate):
    id: int
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str
    role: str
    fahrzeugtyp: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
